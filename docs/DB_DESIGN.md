# 資料庫設計文件 (DB_DESIGN) - 拉屎冠軍爭霸賽系統

本系統使用 SQLite 作為關聯式資料庫。本文件說明了實體關係圖 (ERD)、各資料表欄位定義、SQL 建表語法 (Schema) 以及 Python 模型的 CRUD 設計。

---

## 1. 實體關係圖 (ERD)

以下是資料庫中各實體的關聯關係圖：

```mermaid
erDiagram
    USERS ||--o{ RECORDS : "records (一對多)"
    USERS ||--o{ TOURNAMENTS : "creates (一對多)"
    USERS ||--o{ TOURNAMENT_MEMBERS : "joins (一對多)"
    TOURNAMENTS ||--o{ TOURNAMENT_MEMBERS : "has (一對多)"
    USERS ||--o{ USER_ACHIEVEMENTS : "unlocks (一對多)"
    ACHIEVEMENTS ||--o{ USER_ACHIEVEMENTS : "earned_in (一對多)"

    USERS {
        int id PK
        string username UNIQUE
        string password_hash
        string equipped_title
        int score
        datetime created_at
    }

    RECORDS {
        int id PK
        int user_id FK
        int bristol_type
        string color
        int duration
        string notes
        datetime created_at
    }

    TOURNAMENTS {
        int id PK
        string name
        string code UNIQUE
        int created_by FK
        datetime created_at
    }

    TOURNAMENT_MEMBERS {
        int id PK
        int tournament_id FK
        int user_id FK
        datetime joined_at
    }

    ACHIEVEMENTS {
        int id PK
        string name UNIQUE
        string description
        string condition_type
        int condition_value
    }

    USER_ACHIEVEMENTS {
        int id PK
        int user_id FK
        int achievement_id FK
        datetime unlocked_at
    }
```

---

## 2. 資料表詳細說明

### 2.1 USERS (使用者資料表)
記錄使用者的基本帳戶資訊、總積分以及當前配備的頭銜。

| 欄位名稱 | 資料型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 使用者唯一識別碼 |
| `username` | TEXT | UNIQUE, NOT NULL | 使用者名稱（登入帳號） |
| `password_hash`| TEXT | NOT NULL | 經雜湊加密後的密碼 |
| `equipped_title`| TEXT | DEFAULT '拉屎新手' | 目前配備的趣味稱號 |
| `score` | INTEGER | DEFAULT 0 | 爭霸賽累積積分 |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 註冊時間 |

### 2.2 RECORDS (排便紀錄表)
記錄使用者的排便詳情，包含布里斯托分類及單手表單所記錄的欄位。

| 欄位名稱 | 資料型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 紀錄唯一識別碼 |
| `user_id` | INTEGER | FOREIGN KEY (users.id) | 關聯的使用者 |
| `bristol_type` | INTEGER | NOT NULL | 布里斯托大便分類 (1–7 型) |
| `color` | TEXT | NOT NULL | 便便顏色 (e.g., brown, yellow, green) |
| `duration` | INTEGER | NULL | 排便時長 (秒) |
| `notes` | TEXT | NULL | 備註與碎碎念 |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 紀錄時間 |

### 2.3 TOURNAMENTS (爭霸賽房間表)
使用者可以創建房間，生成邀請碼供他人加入。

| 欄位名稱 | 資料型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 房間唯一識別碼 |
| `name` | TEXT | NOT NULL | 房間名稱 (e.g., "宿舍拉屎天團") |
| `code` | TEXT | UNIQUE, NOT NULL | 6 位數字與字母組成的邀請碼 |
| `created_by` | INTEGER | FOREIGN KEY (users.id) | 創建者 ID |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 創建時間 |

### 2.4 TOURNAMENT_MEMBERS (房間成員關聯表)
記錄使用者加入了哪些爭霸賽房間。

| 欄位名稱 | 資料型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 關聯唯一識別碼 |
| `tournament_id`| INTEGER | FOREIGN KEY (tournaments.id) | 房間 ID |
| `user_id` | INTEGER | FOREIGN KEY (users.id) | 使用者 ID |
| `joined_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 加入房間時間 |

### 2.5 ACHIEVEMENTS (成就設定表)
預先載入的成就條件資料表。

| 欄位名稱 | 資料型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 成就唯一識別碼 |
| `name` | TEXT | UNIQUE, NOT NULL | 成就名稱 (e.g., "煉金術士") |
| `description` | TEXT | NOT NULL | 成就解鎖描述 (e.g., "連續3次拉出黃金第4型") |
| `condition_type`| TEXT | NOT NULL | 觸發檢測類型 (count/type/time) |
| `condition_value`| INTEGER | NOT NULL | 條件觸發閥值 |

### 2.6 USER_ACHIEVEMENTS (使用者成就解鎖紀錄表)
記錄使用者已解鎖的成就。

| 欄位名稱 | 資料型別 | 屬性 | 說明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 解鎖紀錄唯一識別碼 |
| `user_id` | INTEGER | FOREIGN KEY (users.id) | 使用者 ID |
| `achievement_id`| INTEGER | FOREIGN KEY (achievements.id) | 成就 ID |
| `unlocked_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 解鎖時間 |
