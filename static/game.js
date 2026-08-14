var wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
var ws = new WebSocket(wsProtocol + window.location.host);


// DOM 元素
var multiplierEl = document.getElementById("multiplier");
var cashOutBtn = document.getElementById("cashOutBtn");
var betBtn = document.getElementById("betBtn");
var betInput = document.getElementById("betAmount");
var betMinus = document.getElementById("betMinus");
var betPlus = document.getElementById("betPlus");
var balanceDisplay = document.getElementById("balanceDisplay");
var panelMultiplier = document.getElementById("panelMultiplier");
var panelBet = document.getElementById("panelBet");
var panelPayout = document.getElementById("panelPayout");
var livePayout = document.getElementById("livePayout");
var stageStatus = document.getElementById("stageStatus");
var stageBadge = document.getElementById("stageBadge");
var stageMessage = document.getElementById("stageMessage");
var stage = document.getElementById("stage");
var progressFill = document.getElementById("progressFill");
var flashOverlay = document.getElementById("flashOverlay");
var bottleLiquid = document.getElementById("bottleLiquid");
var particlesContainer = document.getElementById("particles");

var currentBet = 0;
var currentMultiplier = 1.0;

// === 粒子系統 ===
function createParticles(count) {
    particlesContainer.innerHTML = '';
    for (var i = 0; i < count; i++) {
        var p = document.createElement('div');
        p.className = 'particle';
        p.style.left = (Math.random() * 100) + '%';
        p.style.top = (40 + Math.random() * 50) + '%';
        p.style.animationDelay = (Math.random() * 4) + 's';
        p.style.animationDuration = (3 + Math.random() * 3) + 's';
        particlesContainer.appendChild(p);
    }
}

// 初始建立少量粒子
createParticles(12);

// === 連線建立 ===
ws.onopen = function() {
    stageMessage.textContent = "空的煉藥台 — 投入金幣以啟動";
};

// === 金額加減按鈕 ===
betMinus.addEventListener("click", function() {
    var val = parseInt(betInput.value) || 100;
    betInput.value = Math.max(10, val - 50);
});

betPlus.addEventListener("click", function() {
    var val = parseInt(betInput.value) || 100;
    betInput.value = val + 50;
});

// === 下注按鈕 ===
betBtn.addEventListener("click", function() {
    var amount = parseFloat(betInput.value);
    if (!amount || amount <= 0) {
        stageMessage.textContent = "請輸入有效金額";
        return;
    }
    currentBet = amount;
    ws.send(JSON.stringify({
        action: "bet",
        player_id: "player1",
        amount: amount
    }));
    betBtn.disabled = true;
    betInput.disabled = true;
    betMinus.disabled = true;
    betPlus.disabled = true;
    panelBet.textContent = amount.toFixed(0);

    // 重設視覺
    multiplierEl.className = "multiplier-display";
    stageMessage.className = "stage-message";
    progressFill.style.width = "0%";
    progressFill.className = "fill";
    bottleLiquid.style.height = "10%";
    bottleLiquid.className = "bottle-liquid";
    stage.className = "stage";
});

// === 接收訊息 ===
ws.onmessage = function(event) {
    var data = JSON.parse(event.data);

    if (data.type === "balance") {
    balanceDisplay.textContent = data.balance.toFixed(1);}
    if (data.type === "game_start") {
        balanceDisplay.textContent = data.balance.toFixed(1);
        stageMessage.textContent = "藥水煉製中...";
        stageMessage.className = "stage-message";
        stageStatus.innerHTML = 'Magic Core <span class="dot">■</span> Brewing';
        stageStatus.className = "stage-status brewing";
        stageBadge.className = "stage-badge visible";
        cashOutBtn.disabled = false;
        stage.className = "stage brewing";

        // 按鈕切換為煉製中狀態
        betBtn.textContent = "煉製中...";
        betBtn.classList.add("brewing");

        // 增加粒子
        createParticles(20);

    } else if (data.type === "tick") {
        currentMultiplier = data.multiplier;
        var display = data.multiplier.toFixed(2) + "x";
        multiplierEl.textContent = display;
        panelMultiplier.textContent = display;
        stageBadge.textContent = display;

        // 倍率跳動動畫
        multiplierEl.classList.remove("tick-bounce");
        void multiplierEl.offsetWidth; // 強制 reflow 重新觸發動畫
        multiplierEl.classList.add("tick-bounce");

        // 可得金額
        var payout = (currentBet * data.multiplier).toFixed(1);
        panelPayout.textContent = payout;
        livePayout.textContent = payout;

        // 藥水液體高度（10% ~ 90%）
        var liquidHeight = Math.min(10 + (data.multiplier - 1) * 15, 90);
        bottleLiquid.style.height = liquidHeight + "%";

        // 風險等級顏色
        multiplierEl.className = "multiplier-display tick-bounce";
        progressFill.className = "fill";
        bottleLiquid.className = "bottle-liquid";

        if (data.multiplier >= 5) {
            multiplierEl.classList.add("risk-high");
            progressFill.classList.add("risk-high");
            bottleLiquid.classList.add("risk-high");
            stageBadge.style.color = "var(--warning-text)";
            stage.className = "stage brewing risk-high";
            createParticles(30);
        } else if (data.multiplier >= 2) {
            multiplierEl.classList.add("risk-medium");
            progressFill.classList.add("risk-medium");
            bottleLiquid.classList.add("risk-medium");
            stageBadge.style.color = "var(--purple-400)";
        } else {
            stageBadge.style.color = "var(--venom-green)";
        }

        // 進度條（風險累積，10x 填滿）
        var progress = Math.min((data.multiplier / 10) * 100, 100);
        progressFill.style.width = progress + "%";

    } else if (data.type === "crash") {
        // 爆炸閃光 + 震動
        flashOverlay.className = "flash-overlay active";
        setTimeout(function() { flashOverlay.className = "flash-overlay"; }, 400);

        multiplierEl.textContent = data.multiplier.toFixed(2) + "x";
        multiplierEl.className = "multiplier-display crashed";
        stageMessage.textContent = "💥 藥水爆炸了！崩潰在 " + data.multiplier.toFixed(2) + "x";
        stageMessage.className = "stage-message fail";
        stageBadge.className = "stage-badge";
        stageStatus.innerHTML = 'Magic Core <span class="dot">■</span> Exploded';
        stageStatus.className = "stage-status";
        stage.className = "stage";
        panelPayout.textContent = "0";
        livePayout.textContent = "0";
        bottleLiquid.style.height = "0%";
        createParticles(8);
        endRound();

    } else if (data.type === "cash_out") {
        // 成功閃光
        flashOverlay.className = "flash-overlay success-flash";
        setTimeout(function() { flashOverlay.className = "flash-overlay"; }, 300);

        multiplierEl.className = "multiplier-display cashed";
        stageMessage.textContent = "✨ 賣出成功！" + data.multiplier.toFixed(2) + " 倍！";
        stageMessage.className = "stage-message success";
        balanceDisplay.textContent = data.balance.toFixed(1);
        stageBadge.className = "stage-badge";
        stageStatus.innerHTML = 'Magic Core <span class="dot">■</span> Complete';
        stageStatus.className = "stage-status";
        stage.className = "stage";
        createParticles(8);
        endRound();

    } else if (data.type === "error") {
        stageMessage.textContent = "❌ " + data.message;
        stageMessage.className = "stage-message fail";
        endRound();
    } 

};

function endRound() {
    cashOutBtn.disabled = true;
    betBtn.disabled = false;
    betBtn.textContent = "開始煉製";
    betBtn.classList.remove("brewing");
    betInput.disabled = false;
    betMinus.disabled = false;
    betPlus.disabled = false;
}

// === Cash Out 按鈕 ===
cashOutBtn.addEventListener("click", function() {
    ws.send("cash_out");
});

// === 斷線 ===
ws.onclose = function() {
    stageMessage.textContent = "連線已斷開";
    stageMessage.className = "stage-message fail";
    cashOutBtn.disabled = true;
    betBtn.disabled = true;
};
