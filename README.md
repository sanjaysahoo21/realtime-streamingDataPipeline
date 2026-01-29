# Real-Time Streaming Data Pipeline

A production-ready real-time data pipeline built with **Apache Spark Streaming**, **Apache Kafka**, and **PostgreSQL**. This project demonstrates end-to-end stream processing with windowed aggregations, sessionization, and multi-sink outputs.

---

## 📋 Project Overview

This pipeline ingests user activity events from Kafka, processes them in real-time using Spark Structured Streaming, and outputs results to multiple destinations:

- **PostgreSQL**: Stores aggregated metrics (page views, active users, sessions)
- **Data Lake**: Archives raw events in Parquet format
- **Kafka**: Publishes enriched events for downstream consumers

### Key Features

✅ **Windowed Aggregations**
- 1-minute tumbling windows for page view counts
- 5-minute sliding windows for active user tracking

✅ **Session Tracking**
- Native Spark session windows (5-minute gap)
- Automatic session duration calculation

✅ **Fault Tolerance**
- Idempotent writes to PostgreSQL using UPSERT
- Watermarking (2 minutes) for handling late-arriving data
- Checkpointing for exactly-once processing

✅ **Scalable Architecture**
- Fully containerized with Docker Compose
- Horizontal scaling ready
- Production-grade error handling

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for running producers)
- 4GB+ RAM recommended

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd realtime-streamingDataPipeline
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Start the services**
   ```bash
   docker compose up -d
   ```

   This will start:
   - Zookeeper (port 2181)
   - Kafka (port 9092, external 29092)
   - PostgreSQL (port 5433)
   - Spark Streaming Application

4. **Verify services are running**
   ```bash
   docker compose ps
   ```

### Running the Pipeline

#### Step 1: Generate Sample Data

Run the time-series producer to simulate realistic user activity:

```bash
docker run --rm --network host \
  -v "$(pwd)/producer:/app" -w /app \
  python:3.9-slim bash -c \
  "pip install kafka-python && python time_series_producer.py"
```

This generates 15 minutes of simulated events with timestamps spread across time.

#### Step 2: Monitor Spark Processing

```bash
docker compose logs -f spark-app
```

You should see logs indicating batch processing and data writes.

#### Step 3: Query Results

**Page View Counts:**
```bash
docker exec db psql -U postgres -d stream_data -c \
  "SELECT * FROM page_view_counts ORDER BY window_start DESC LIMIT 5;"
```

**Active Users:**
```bash
docker exec db psql -U postgres -d stream_data -c \
  "SELECT * FROM active_users ORDER BY window_start DESC LIMIT 5;"
```

**User Sessions:**
```bash
docker exec db psql -U postgres -d stream_data -c \
  "SELECT * FROM user_sessions ORDER BY session_start_time DESC LIMIT 5;"
```

---

## 📊 Demo Outputs

### Page View Counts (1-Minute Windows)

```
    window_start     |     window_end      | page_url  | view_count 
---------------------+---------------------+-----------+------------
 2026-01-29 09:42:00 | 2026-01-29 09:43:00 | /profile  |          2
 2026-01-29 09:42:00 | 2026-01-29 09:43:00 | /products |          1
 2026-01-29 09:42:00 | 2026-01-29 09:43:00 | /home     |          1
 2026-01-29 09:27:00 | 2026-01-29 09:28:00 | /cart     |          4
 2026-01-29 09:27:00 | 2026-01-29 09:28:00 | /home     |          3
```

### Active Users (5-Minute Sliding Windows)

```
    window_start     |     window_end      | active_users_count 
---------------------+---------------------+--------------------
 2026-01-29 09:36:00 | 2026-01-29 09:41:00 |                  4
 2026-01-29 09:35:00 | 2026-01-29 09:40:00 |                  4
 2026-01-29 09:34:00 | 2026-01-29 09:39:00 |                  4
```

### Enriched Kafka Messages

Messages in the `enriched_activity` topic include processing timestamps:

```json
{
  "event_time": "2026-01-29T09:31:03.027Z",
  "user_id": "user_1",
  "page_url": "/cart",
  "event_type": "page_view",
  "processing_time": "2026-01-29T09:31:23.328Z"
}
```

---

## 🏗️ Architecture

```
┌─────────────┐
│   Producer  │
│  (Python)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────────┐
│    Kafka    │─────▶│  Spark Streaming │
│ user_activity│      │   (PySpark 3.5)  │
└─────────────┘      └────────┬─────────┘
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
          ┌──────────┐  ┌─────────┐  ┌─────────┐
          │PostgreSQL│  │Data Lake│  │  Kafka  │
          │ (Metrics)│  │(Parquet)│  │enriched │
          └──────────┘  └─────────┘  └─────────┘
```

### Data Flow

1. **Ingestion**: Python producer sends events to `user_activity` Kafka topic
2. **Processing**: Spark reads from Kafka, applies transformations:
   - Watermarking for late data handling
   - Tumbling/sliding window aggregations
   - Session window tracking
3. **Output**: Results written to PostgreSQL, Data Lake, and Kafka

---

## 🛠️ Technical Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Stream Processing | Apache Spark | 3.5.0 |
| Message Queue | Apache Kafka | Latest |
| Database | PostgreSQL | Latest |
| Orchestration | Docker Compose | - |
| Language | Python | 3.9+ |

### Key Dependencies

- **PySpark**: Structured Streaming API
- **pandas**: 1.5.3 (pinned for compatibility)
- **pyarrow**: 11.0.0 (pinned for compatibility)
- **psycopg2-binary**: PostgreSQL adapter
- **kafka-python**: Producer client

---

## 📁 Project Structure

```
.
├── docker-compose.yml          # Service orchestration
├── init-db.sql                 # PostgreSQL schema
├── .env.example                # Environment template
├── spark/
│   ├── Dockerfile              # Spark image with dependencies
│   └── app/
│       └── main.py             # Streaming application logic
├── producer/
│   ├── producer.py             # Basic event generator
│   ├── time_series_producer.py # Time-spread simulation
│   ├── full_producer.py        # High-volume traffic
│   └── finalizer_producer.py   # Window closure helper
└── data/
    ├── checkpoints/            # Spark checkpoints (gitignored)
    └── lake/                   # Parquet output (gitignored)
```

---

## 🔧 Configuration

### Database Schema

The pipeline creates three tables in PostgreSQL:

**page_view_counts**
```sql
CREATE TABLE page_view_counts (
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    page_url VARCHAR(255),
    view_count BIGINT,
    PRIMARY KEY (window_start, page_url)
);
```

**active_users**
```sql
CREATE TABLE active_users (
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    active_users_count BIGINT,
    PRIMARY KEY (window_start)
);
```

**user_sessions**
```sql
CREATE TABLE user_sessions (
    user_id VARCHAR(50),
    session_start_time TIMESTAMP,
    session_end_time TIMESTAMP,
    session_duration_seconds BIGINT,
    PRIMARY KEY (user_id, session_start_time)
);
```

### Environment Variables

Create a `.env` file with:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=stream_data
```

---

## 🐛 Troubleshooting

### Issue: Spark container crashes

**Solution**: Ensure you have at least 4GB RAM allocated to Docker.

### Issue: Empty database tables

**Solution**: 
1. Check Spark logs: `docker compose logs spark-app`
2. Verify Kafka topic exists: `docker exec kafka kafka-topics --list --bootstrap-server kafka:9092`
3. Run the time-series producer to generate events with proper timestamps

### Issue: "Permission denied" errors

**Solution**: Run `chmod -R 777 data/` to fix permissions on checkpoint/lake directories.

---

## 🎯 Conclusion

This project demonstrates a complete real-time data pipeline capable of:

- **Processing millions of events per day** with low latency
- **Handling out-of-order data** through watermarking
- **Ensuring data consistency** with idempotent writes
- **Scaling horizontally** by adding more Spark workers

### Use Cases

- **E-commerce Analytics**: Track user behavior, cart abandonment, conversion funnels
- **IoT Monitoring**: Process sensor data, detect anomalies, trigger alerts
- **Financial Services**: Fraud detection, transaction monitoring, risk analysis
- **Social Media**: Engagement metrics, trending topics, user activity tracking

### Next Steps

- Add **Grafana dashboards** for real-time visualization
- Implement **alerting** with Prometheus
- Deploy to **Kubernetes** for production
- Add **machine learning** models for predictions

---

## 📝 License

This project is open-source and available under the MIT License.

## 👥 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

**Built with ❤️ using Apache Spark and Kafka**