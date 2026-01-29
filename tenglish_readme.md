# Real-Time Streaming Data Pipeline (Tenglish Version)

Hello Andi! 👋 Ee project oka **Real-Time Data Pipeline**. Ante data ni ventane process chesi, results ni quick ga ivvadam annamata. Deeniki manam **Apache Spark**, **Kafka**, mariyu **PostgreSQL** vaadanu.

Asalu ee project enti, enduku chesam, ela panichestundo clear ga explain chestanu chudandi below.

---

## 🧐 1. Asalu Ee Project Enti? (What?)

Idhi oka complete data pipeline system andi.
1. Users website lo em chestunnaro (clicks, page views) ah data **Kafka** loki vastundi.
2. Akkadnunchi **Spark Streaming** ah data ni teesukoni, real-time lo calculate chestundi.
3. Final ga results ni **PostgreSQL DB** lo mariyu **Data Lake** lo save chestundi.

Deeniloj manam mainly 3 calculations chestunnam:
* **Page Views**: Ee nimisham lo ye page ekkuva mandi chustunnaru?
* **Active Users**: Prati 5 minutes ki entha mandi users active ga unnaru?
* **User Sessions**: Okka user entha sepu website lo unnaru (Session Duration)?

---

## 🤷 2. Enduku Ee Project? (Why?)

* **Speed**: Business decisions teskovalante data late ga vasthe labham ledu. Ventane ravali.
* **Tracking**: Evaru em chestunnaro telusukovadam chala important (Analytics).
* **Automation**: Manam manual ga calcualte cheyakunda, automatic ga system ye anni lekka petti database lo pedutundi.
* **Learning**: Big Data technologies like Spark & Kafka ela work avtayo nerchukovadaniki idi best project.

---

## 🛠️ 3. Ee Project Lo Emem unnai? (Tools Used)

Ekkada major ga 4 tools vaadam:

| Tool | Pani Enti? (Role) | Example |
|------|-------------------|---------|
| **Apache Kafka** | Data ni first collect chesi, queue lo pedutundi. | Postman laga, messages ni carry chestundi. |
| **Apache Spark** | Main brain idhe. Data ni process chesi, calculations chestundi. | Calculator + Processor annamata. |
| **PostgreSQL** | Process ayina data ni final ga store chestundi. | Mana results store room. |
| **Docker** | Annitini kalipi okesari run cheyadaniki help avtundi. |  Container, anni pakkana pakka petti run chestundi. |

---

## 📂 4. Project Lo Files Ememunnai? (Project Structure)

Manam create chesina files list idi:

*   **`docker-compose.yml`**: Idi mana master plan. Kafka, Spark, DB anni elaa start avalo indulo rasam.
*   **`spark/Dockerfile`**: Spark ki kavalsina dependencies (Python libraries, Drivers) anni indulo install chesam.
*   **`spark/app/main.py`**: **Core Logic** ikkade undi. Spark data ni ela read cheyali, ela process cheyali anedi ikkade rasaam.
*   **`producer/`**:
    *   `producer.py`: Simple ga data generate chestundi.
    *   `full_producer.py`: Ekkuva traffic (Users) ni simulate chestundi.
*   **`init-db.sql`**: Database lo tables (columns, rows) create cheyadaniki use ayye script.

---

## 🔄 5. Project Flow Ela Untundi? (How it Works?)

Motham process 3 steps lo jarugutundi:

### Step 1: Input (Data Ingestion)
Mana producer script (`producer.py`) fake user events ni create chestundi. E.g., *"User1 home page chusaaru"*.
Ee data ni **Kafka** lo `user_activity` ane **Topic** ki pampistundi.

### Step 2: Processing (The Engine)
Mana **Spark App** (`main.py`) Kafka nunchi aa data ni *Live* ga chaduvutundi.
Ah data meeda *Windows* apply chestundi:
> "Gata 1 minute lo enni views vachayi?"
> "User session eppudu start ayindi, eppudu end ayindi?"

### Step 3: Output (Destination)
Calculate chesina answers ni 3 chotla save chestundi:
1.  **PostgreSQL**: Tables lo counts save avtay. (Manam SQL queries tho easy ga chudachu).
2.  **Data Lake**: Raw data ni files ga save chestundi (`parquet` format lo). Future lo use avtundi.
3.  **Kafka Output**: Process ayina data ni malli Kafka lo `enriched_activity` topic ki pampistundi (vere applications vadukodaniki).

---

## 🚀 6. Ela Run Cheyali? (How to Start?)

Simple ga ee steps follow avvandi:

1.  **Start Services**:
    Docker tho anni start cheyandi.
    ```bash
    docker compose up -d
    ```

2.  **Generate Data (Producer)**:
    Fake traffic ni generate cheyandi.
    ```bash
    # Idi run chestene data vastundi
    docker run --rm --network host -v "$(pwd)/producer:/app" -w /app python:3.9-slim bash -c "pip install kafka-python && python full_producer.py"
    ```

3.  **Check Results**:
    Database lo em save ayindo chudandi.
    ```bash
    docker exec db psql -U postgres -d stream_data -c "SELECT * FROM page_view_counts;"
    ```

Anthe! Mee pipeline ready ga undi. 🎉

---

## ✨ Conclusion

Ee project dwara manam Real-time data ni ela handle cheyalo, database lo ela veyyalo nerchukunnam. Ide concept ni pedda companies like Netflix, Uber vaalla data pipelines kosam vadutaru.

**Happy Coding! 🚀**
