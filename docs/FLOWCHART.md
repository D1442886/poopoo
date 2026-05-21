# [拉屎冠軍爭霸賽] 會員與戰隊系統 — 流程圖與路由設計 (FLOWCHART)

> [!NOTE]
> 本文件根據 [PRD 需求](file:///c:/Users/User/Desktop/poopoo/docs/PRD.md) 與 [ARCHITECTURE 設計](file:///c:/Users/User/Desktop/poopoo/docs/ARCHITECTURE.md)，繪製使用者操作路徑之 **使用者流程圖 (User Flow)**、系統後端處理與資料庫存取的 **系統序列圖 (Sequence Diagram)**，並彙整 **功能與路由對照表**。

---

## 1. 使用者流程圖 (User Flow)

此圖描述使用者從進入網頁開始，經歷身份檢查、註冊（含戰隊綁定）、登入、進入個人儀表板、到切換戰隊或登出的完整操作路徑。

```mermaid
flowchart TD
    Start([使用者開啟網頁]) --> CheckLogin{是否已登入？}
    
    CheckLogin -- 已登入 --> Dashboard[儀表板 /dashboard]
    CheckLogin -- 未登入 --> LoginView[登入頁面 /login]
    
    LoginView --> ChooseAction{想要做什麼？}
    
    ChooseAction -- 登入 --> DoLogin[輸入帳密並登入]
    ChooseAction -- 沒有帳號，去註冊 --> RegisterView[註冊與選擇戰隊 /register]
    
    %% 註冊流程
    RegisterView --> InputReg[填寫註冊資料與挑選戰隊]
    Note over InputReg: 包含欄位：帳號、密碼、暱稱<br/>並從下拉選單選取戰隊 (高纖/多水)
    InputReg --> SubmitReg[送出註冊表單]
    SubmitReg --> ValReg{驗證是否通過？}
    
    ValReg -- 帳號重複或格式錯誤 --> RegFail[顯示錯誤訊息]
    RegFail --> RegisterView
    
    ValReg -- 成功建立帳號 --> AutoLogin[系統自動登入並建立 Session]
    AutoLogin --> Dashboard
    
    %% 登入流程
    DoLogin --> SubmitLogin[送出登入表單]
    SubmitLogin --> ValLogin{帳號與密碼比對？}
    
    ValLogin -- 密碼錯誤或帳號不存在 --> LoginFail[顯示登入失敗提示]
    LoginFail --> LoginView
    
    ValLogin -- 比對成功 --> SetSession[寫入用戶 Session]
    SetSession --> Dashboard
    
    %% 儀表板操作
    Dashboard --> DashboardAction{在儀表板的操作？}
    
    DashboardAction -- 1. 查看狀態 --> ViewStats[瀏覽個人資訊與所屬戰隊資訊]
    DashboardAction -- 2. 切換戰隊 --> ChangeClan[POST /join-clan 更改戰隊]
    DashboardAction -- 3. 登出系統 --> Logout[GET /logout 清除 Session]
    
    ChangeClan --> UpdateClanDB[更新資料庫中的戰隊綁定]
    UpdateClanDB --> Dashboard
    
    Logout --> LoginView
```

---

## 2. 系統序列圖 (Sequence Diagram)

這裡繪製核心後端寫入功能：**用戶註冊與戰隊資料庫關聯寫入的完整系統生命週期流程**。

```mermaid
sequenceDiagram
    autonumber
    actor User as 使用者瀏覽器
    participant Flask as Flask Controller<br/>(app/routes/auth.py)
    participant Model as User Model<br/>(app/models/user.py)
    participant DB as SQLite3 封裝<br/>(app/models/db.py)
    database SQLite as SQLite Database<br/>(instance/database.db)

    User->>Flask: GET /register (請求註冊與戰隊頁面)
    Flask->>DB: get_db_connection()
    DB->>SQLite: 查詢所有戰隊清單 (SELECT * FROM clans)
    SQLite-->>DB: 回傳戰隊資料 (Id, 名稱, 說明)
    DB-->>Flask: 戰隊清單物件 list
    Flask-->>User: 渲染並返回 register.html (帶入戰隊選項)

    User->>Flask: POST /register (提交 username, password, nickname, clan_id)
    
    Note over Flask: 1. 欄位防呆（長度、必填檢查）<br/>2. 使用 Werkzeug generate_password_hash 加密密碼
    
    Flask->>Model: create_user(username, hashed_password, nickname, clan_id)
    Model->>DB: get_db_connection()
    
    Model->>SQLite: 查詢該 username 是否已被佔用
    SQLite-->>Model: 回傳查詢筆數
    
    alt 帳號已存在 (重疊)
        Model-->>Flask: 拋出 UsernameExistsError
        Flask-->>User: 渲染 register.html (Flash 顯示「帳號已被使用」)
    else 帳號唯一 (正常寫入)
        Model->>SQLite: INSERT INTO users (username, password, nickname, clan_id)<br/>Values (?, ?, ?, ?)
        SQLite-->>Model: 寫入成功確認與回傳 rowid (user_id)
        Model-->>Flask: 回傳註冊成功 (user_id)
        
        Note over Flask: 將 user_id 寫入 Flask Session<br/>session['user_id'] = user_id
        
        Flask-->>User: Redirect 302 重導向至 /dashboard
    end
```

---

## 3. 功能清單與路由對照表

本模組預計開發的 URL 路由與 HTTP 請求對照表如下：

| 功能名稱 | 請求 URL | HTTP 方法 | 對應模板 (View) | Controller 路由處置 (Controller) | 備註 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **首頁 / 儀表板** | `/dashboard` | `GET` | `templates/index.html` | `app/routes/main.py` | 顯示當前登入者資訊、所屬戰隊以及戰隊資訊。若未登入則導向 `/login`。 |
| **註冊頁面渲染** | `/register` | `GET` | `templates/register.html` | `app/routes/auth.py` | 載入並渲染註冊表單，後端會撈取 `clans` 清單渲染成下拉選單。 |
| **註冊表單提交** | `/register` | `POST` | *無（重導向）* | `app/routes/auth.py` | 驗證輸入、雜湊密碼、防重檢查並將用戶與選定 `clan_id` 寫入資料庫。 |
| **登入頁面渲染** | `/login` | `GET` | `templates/login.html` | `app/routes/auth.py` | 渲染會員登入介面。 |
| **登入表單提交** | `/login` | `POST` | *無（重導向）* | `app/routes/auth.py` | 驗證帳密並建立登入 Session，跳轉至 `/dashboard`。 |
| **變更戰隊** | `/join-clan` | `POST` | *無（重導向）* | `app/routes/clan.py` | 讓已登入的使用者在儀表板更新自己綁定的戰隊 ID。 |
| **登出帳號** | `/logout` | `GET` | *無（重導向）* | `app/routes/auth.py` | 清除 Session 並重導向回 `/login`。 |

---
*本流程圖文件由 Antigravity 輔助建構，為「拉屎冠軍爭霸賽」的資料流轉與邏輯順序提供視覺化支撐。*
