FROM apache/spark:3.5.0

USER root
WORKDIR /app

COPY app /app

RUN pip install "pandas==1.5.3" "pyarrow==11.0.0" psycopg2-binary

CMD ["/opt/spark/bin/spark-submit", \
    "--packages", \
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.6.0", \
    "main.py"]
