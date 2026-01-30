from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, to_timestamp, current_timestamp, 
    window, count, countDistinct, to_json, struct, to_date, session_window, min, max
)
from pyspark.sql.types import (
    StructType, StructField, StringType, TimestampType, LongType
)
# from pyspark.sql.streaming import GroupStateTimeout
import pandas as pd
import os
# import psycopg2  

spark = SparkSession.builder \
    .appName("RealtimePipeline") \
    .config("spark.sql.session.timeZone", "UTC") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ----------------------------
# Configuration
# ----------------------------
DB_NAME = os.getenv("DB_NAME", "stream_data")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = "db"
DB_PORT = "5432"

def get_db_connection():
    import psycopg2
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# ----------------------------
# Schema
# ----------------------------
schema = StructType([
    StructField("event_time", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("page_url", StringType(), True),
    StructField("event_type", StringType(), True)
])

# ----------------------------
# Read from Kafka
# ----------------------------
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "user_activity") \
    .option("startingOffsets", "latest") \
    .load()

parsed_df = raw_df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

events_df = parsed_df.withColumn(
    "event_time",
    to_timestamp(col("event_time"))
).withWatermark("event_time", "2 minutes")

# ----------------------------
# Helper: Idempotent DB Writer
# ----------------------------
def write_to_postgres(batch_df, batch_id, table_name, pk_cols, update_cols):
    """
    Writes a batch DataFrame to PostgreSQL using INSERT ON CONFLICT (UPSERT).
    """
    def process_partition(iterator):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            for row in iterator:
                columns = list(row.asDict().keys())
                values = [row[col] for col in columns]
                
                # Construct SQL
                cols_str = ", ".join(columns)
                placeholders = ", ".join(["%s"] * len(values))
                
                # ON CONFLICT clause
                pk_str = ", ".join(pk_cols)
                update_set = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_cols])
                
                sql = f"""
                    INSERT INTO {table_name} ({cols_str})
                    VALUES ({placeholders})
                    ON CONFLICT ({pk_str})
                    DO UPDATE SET {update_set};
                """
                
                cur.execute(sql, values)
            
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error writing to DB: {e}")
            # In production, handle correctly (retry or DLQ)

    batch_df.foreachPartition(process_partition)

# ----------------------------
# 1. Page View Counts (Tumbling Window 1 min)
# ----------------------------
page_counts_df = events_df \
    .where(col("event_type") == "page_view") \
    .groupBy(window("event_time", "1 minute"), "page_url") \
    .count() \
    .select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("page_url"),
        col("count").alias("view_count")
    )

q1 = page_counts_df.writeStream \
    .foreachBatch(lambda df, id: write_to_postgres(df, id, "page_view_counts", ["window_start", "page_url"], ["view_count"])) \
    .outputMode("update") \
    .option("checkpointLocation", "/opt/spark/data/checkpoints/page_views") \
    .start()

# ----------------------------
# 2. Active Users (Sliding Window 5 min, slide 1 min)
# ----------------------------
from pyspark.sql.functions import approx_count_distinct

active_users_df = events_df \
    .groupBy(window("event_time", "5 minutes", "1 minute")) \
    .agg(approx_count_distinct("user_id").alias("active_user_count")) \
    .select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("active_user_count")
    )

q2 = active_users_df.writeStream \
    .foreachBatch(lambda df, id: write_to_postgres(df, id, "active_users", ["window_start"], ["active_user_count"])) \
    .outputMode("update") \
    .option("checkpointLocation", "/opt/spark/data/checkpoints/active_users") \
    .start()

# ----------------------------
# 3. Session State (Native Spark Session Window)
# ----------------------------
sessions_df = events_df \
    .groupBy(
        session_window(col("event_time"), "5 minutes"),
        col("user_id")
    ) \
    .agg(
        min("event_time").alias("session_start_time"),
        max("event_time").alias("session_end_time"),
        count("*").alias("event_count")
    ) \
    .select(
        col("user_id"),
        col("session_start_time"),
        col("session_end_time"),
        (col("session_end_time").cast("long") - col("session_start_time").cast("long")).alias("session_duration_seconds")
    )

q3 = sessions_df.writeStream \
    .foreachBatch(lambda df, id: write_to_postgres(df, id, "user_sessions", ["user_id"], ["session_start_time", "session_end_time", "session_duration_seconds"])) \
    .outputMode("append") \
    .option("checkpointLocation", "/opt/spark/data/checkpoints/user_sessions") \
    .start()

# ----------------------------
# 4. Enriched Data -> Kafka & Data Lake
# ----------------------------
enriched_df = events_df.withColumn("processing_time", current_timestamp())

def write_enriched_and_lake(batch_df, batch_id):
    # Persist allows caching since we use it twice
    batch_df.persist()
    
    # 1. Write to Kafka
    batch_df.select(to_json(struct("*")).alias("value")) \
        .write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("topic", "enriched_activity") \
        .save()
        
    # 2. Write to Data Lake
    batch_df.withColumn("event_date", to_date("event_time")) \
        .write \
        .partitionBy("event_date") \
        .mode("append") \
        .parquet("/opt/spark/data/lake")
        
    batch_df.unpersist()

q4 = enriched_df.writeStream \
    .foreachBatch(write_enriched_and_lake) \
    .outputMode("append") \
    .option("checkpointLocation", "/opt/spark/data/checkpoints/enriched") \
    .start()

spark.streams.awaitAnyTermination()
