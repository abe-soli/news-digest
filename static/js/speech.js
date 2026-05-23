// Web Speech APIによる読み上げ機能
let isSpeaking = false;
let textQueue = [];
let currentIndex = 0;

/**
 * 全記事のsummaryを順番に読み上げる
 * @param {Array<string>} summaries - 読み上げるsummaryの配列
 */
function speakAllArticles(summaries) {
  // 既に読み上げ中の場合は停止
  if (isSpeaking) {
    stopSpeaking();
    return;
  }

  if (!summaries || summaries.length === 0) {
    return;
  }

  textQueue = summaries;
  currentIndex = 0;
  speakNext();
}

/**
 * 次のテキストを読み上げる
 */
function speakNext() {
  if (currentIndex >= textQueue.length) {
    // 全て読み上げ終了
    isSpeaking = false;
    textQueue = [];
    currentIndex = 0;
    updateButtonStates(false);
    return;
  }

  const text = textQueue[currentIndex];
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'ja-JP';
  utterance.rate = 1.5; // 読み上げ速度

  // 読み上げ開始時の処理
  utterance.onstart = () => {
    isSpeaking = true;
    updateButtonStates(true);
  };

  // 読み上げ終了時の処理
  utterance.onend = () => {
    currentIndex++;
    speakNext();
  };

  // エラー時の処理
  utterance.onerror = (event) => {
    console.error('読み上げエラー:', event.error);
    currentIndex++;
    speakNext();
  };

  speechSynthesis.speak(utterance);
}

/**
 * 読み上げを停止する
 */
function stopSpeaking() {
  if (speechSynthesis.speaking || speechSynthesis.pending) {
    speechSynthesis.cancel();
  }
  isSpeaking = false;
  textQueue = [];
  currentIndex = 0;
  updateButtonStates(false);
}

/**
 * ボタンの状態を更新する
 * @param {boolean} speaking - 読み上げ中かどうか
 */
function updateButtonStates(speaking) {
  const speakButton = document.getElementById('speak-all-btn');
  const stopButton = document.getElementById('stop-all-btn');

  if (speakButton) {
    speakButton.disabled = speaking;
  }
  if (stopButton) {
    stopButton.disabled = !speaking;
  }
}
