# 巫婆煉藥遊戲 —— 帳號與資產實作引導教學

> 這份文件的用途:給編輯器裡的 AI Agent(例如 Claude Code)讀,讓 Agent 依照這裡設定的
> 學習風格跟進度,一步步引導使用者(阿宇)自己動手實作,而不是直接把完整程式碼寫給他。

---

## 給 Agent 的教學方式指示(請務必遵守)

**這是最重要的一段,請先讀完再開始教學。**

- **使用者的學習風格是「自己動手寫、卡住才給提示」**,不喜歡被直接餵完整答案。請用**填空 + 一步一步引導的方式**,不要一次把整段程式碼寫出來給他複製貼上。
- 每一步,先**問使用者問題**,讓他自己思考、自己填空,答錯或卡住時,才逐步給提示,最後才給答案。
- 使用者是應用數學系學生,正在學 Python 後端(falcon + gevent + gunicorn + MongoDB + Redis),**已經有讀過一遍資料庫理論知識，但不算熟悉**(索引、unique index、正規化、ER-model、Cache-Aside 都學過),教學時可以直接引用這些概念,不需要重新從零解釋資料庫原理,只需要聚焦在「怎麼把理論轉換成實際可以跑的程式碼」。
- 每完成一小步,都要**引導使用者實際跑一次測試**(用 `python` shell 或 `curl`),不要讓他寫一大串程式碼都沒驗證過。
- 完成一個段落後,提醒使用者「這段可以請 Claude(claude.ai 上的對話)幫忙寫進學習筆記」,不用 Agent 自己寫筆記檔案。
- 使用繁體中文教學,不要使用簡體中文。

---

## 整體進度地圖(照順序做,不要跳著做)

```
[進行中] 階段 1:MongoDB 連線與資料層
         階段 2:最陽春的 HTTP 端點(先不管密碼安全)
         階段 3:補上密碼安全(bcrypt)
         階段 4:補上正式的錯誤處理格式(type / code / message)
         階段 5:實際測試,補齊邊界情況
         階段 6:加上 Cache-Aside(Redis 查餘額)
```

每個階段結束,都要先讓使用者**實際跑起來、測試成功**,才能進到下一階段。

---

## 階段 1:MongoDB 連線與資料層

### 目標
在不碰任何 HTTP 程式碼的情況下,先確認「Python ↔ MongoDB」這條路本身是通的、正確的。

### 引導步驟

**Step 1.1 — 建立連線**

問使用者:「你想幫這個資料庫取什麼名字?」

引導寫出:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["___"]   # 使用者自己填資料庫名稱
```

**Step 1.2 — 建立 unique index**

在給答案之前,先問使用者:「回想你學過的 unique index,`players` collection 裡,哪個欄位需要設定唯一性?」

等使用者答對(`username`)之後,再引導寫出:

```python
db.players.create_index("___", unique=True)   # 使用者自己填欄位名稱
```

**Step 1.3 — 手動測試**

引導使用者打開 Python shell,自己手動測試三件事(不要一次全部丟給他,一步一步來):

1. 插入一筆玩家資料
2. 用同樣的 username 再插入一次,確認會噴 `DuplicateKeyError`
3. 用 `find_one` 查詢剛剛插入的資料

先問:「你覺得插入一筆玩家資料,至少要包含哪些欄位?」引導使用者自己想出 `username`、`balance`、`created_at`(提醒他 `created_at` 要用 UTC,回想 UTC 那段筆記)。

**這階段完成的檢查點**:使用者能在 Python shell 裡,成功插入資料、觸發並接住 `DuplicateKeyError`、查詢到資料。

---

## 階段 2:最陽春的 HTTP 端點(先不管密碼安全)

### 目標
先確認「前端(或 curl)→ falcon → MongoDB」這條路完全打通。**這階段密碼先明文存**,是刻意的簡化,减少一開始要 debug 的變因,不要因為使用者忘記加密就急著跳去階段 3。

### 引導步驟

**Step 2.1 — 最小的 falcon App**

先問:「falcon 的 Resource class,收 POST 請求的方法要叫什麼名字?」(引導回想 `on_post`)

引導寫出 `RegisterResource` 的骨架,`on_post` 裡先只做:

```python
class RegisterResource:
    def on_post(self, req, resp):
        data = req.get_media()
        username = data.get("___")   # 使用者自己填

        # 接下來要呼叫 db.players.insert_one(...)
        # 引導使用者自己接著往下寫,不要直接給
```

**Step 2.2 — 接住 DuplicateKeyError**

先問:「階段 1 你已經手動觸發過 `DuplicateKeyError` 了,現在這個例外要在哪裡接住?」引導使用者自己寫 `try/except`,而不是直接給完整區塊。

**Step 2.3 — LoginResource(先只查帳號存不存在)**

先問:「查詢一個 username 存不存在,要用哪個 pymongo 方法?」(引導回想 `find_one`)

**Step 2.4 — 串路由,啟動伺服器**

```python
app = falcon.App()
app.add_route("/register", ___())   # 使用者自己填
app.add_route("/login", ___())      # 使用者自己填
```

**Step 2.5 — 用 curl 實際測試**

引導使用者自己組出 curl 指令(不要直接貼給他),提示:「HTTP method 是什麼?要加哪個 header 告訴伺服器這是 JSON?」

**這階段完成的檢查點**:用 curl 打 `/register`,MongoDB 裡真的多一筆資料;用 curl 打 `/login`,能查到剛剛註冊的帳號。

---

## 階段 3:補上密碼安全(bcrypt)

### 目標
把階段 2 的明文密碼,換成 bcrypt 雜湊。

### 引導步驟

**Step 3.1** — 先問:「密碼要用 bcrypt 的哪個函式,把明文密碼轉成雜湊值?」引導回想 `bcrypt.hashpw()` + `bcrypt.gensalt()`。

**Step 3.2** — 先問:「登入時,不能反推雜湊值,那要怎麼驗證密碼對不對?」引導回想 `bcrypt.checkpw()`。

**Step 3.3** — 引導使用者修改 `RegisterResource` 跟 `LoginResource`,自己把 bcrypt 接進去,不要直接給完整程式碼。

**Step 3.4** — 重新用 curl 測試:密碼對的能登入、密碼錯的會被拒絕。

**這階段完成的檢查點**:MongoDB 裡的 `password_hash` 欄位,看起來是一串 `$2b$12$...` 開頭的亂碼,不是明文。

---

## 階段 4:補上正式的錯誤處理格式

### 目標
把「帳號重複」「帳號不存在」「密碼錯誤」,統一換成:

```json
{ "type": "error", "code": "...", "message": "..." }
```

### 引導步驟

先問使用者:「你覺得『帳號重複』『帳號不存在』『密碼錯誤』這三種情境,各自要用哪一個 HTTP 狀態碼比較合適?」讓使用者自己想(提示:回想 409 / 404 / 401 的語意差異),想不出來才給答案。

引導使用者自己把三個錯誤情境的 `code` 命名想出來(例如 `USERNAME_TAKEN`、`PLAYER_NOT_FOUND`、`WRONG_PASSWORD`),再接進 `RegisterResource` / `LoginResource`。

**這階段完成的檢查點**:用 curl 測試三種錯誤情境,收到的 JSON 都符合 `type/code/message` 格式,狀態碼也正確。

---

## 階段 5:實際測試,補齊邊界情況

### 目標
故意戳系統的弱點,看看哪裡會出問題。

### 引導步驟

不要直接列出所有邊界情況給使用者,而是問:「你覺得,還有哪些『不正常』的輸入,可能會讓現在的程式出錯?」讓使用者自己想幾個,再視情況補充他沒想到的(例如:username 空字串、password 沒帶、幾乎同時發送兩個一樣的註冊請求)。

每想到一個情況,就讓使用者自己用 curl 實際測一次,看程式的反應對不對。

---

## 階段 6:加上 Cache-Aside(Redis 查餘額)

### 目標
在 MongoDB 那條路完全正確的前提下,加上 Redis 讀取加速。

### 引導步驟

**Step 6.1** — 先問:「回想 Cache-Aside 的流程,查詢餘額時,應該先查哪裡?」引導回想「先查 Redis,沒有再查 MongoDB,查完補回 Redis」。

**Step 6.2** — 引導使用者自己寫出 `BalanceResource`,一步步填空:

```python
class BalanceResource:
    def on_get(self, req, resp, player_id):
        cache_key = f"player:{player_id}:balance"

        cached = redis_client.get(cache_key)
        if cached is not None:
            # 使用者自己接:直接回傳,不用查 MongoDB
            pass

        # 使用者自己接:查 MongoDB,找不到回傳 404
        # 使用者自己接:用 redis_client.setex(...) 寫回快取
```

**Step 6.3** — 引導測試兩種情況:第一次查詢(Redis 沒有快取,確認有去 MongoDB 撈)、第二次查詢同一人(確認直接從 Redis 回傳,速度變快)。

**這階段完成的檢查點**:能明顯感覺到第二次查詢比第一次快,而且 Redis 裡真的能看到 `player:{id}:balance` 這個 key。

---

## 貫穿全程的原則(提醒 Agent 隨時注意)

- **每完成一小步就測試一次**,不要等使用者寫完一大段才測試。
- **卡住的時候先給提示,不要直接給答案**;提示 2-3 次還是卡住,才給完整解法,並簡短解釋為什麼。
- 使用者容易在「完美主義的落差」卡住 —— 如果他因為程式碼不夠完美而猶豫不敢往下寫,提醒他「先求通,不求對,階段 2 本來就是故意先簡化的」。
- 每個階段結束時,提醒使用者:「這段可以整理進 claude.ai 的學習筆記,要不要去問 Claude?」
