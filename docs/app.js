let gameData;
let guessCount = 0;
let guessed = false;

// Load game data from backend
async function loadGameData() {
  const res = await fetch('https://ap-backend-dk63bddqmjcm5qwn9ktntp.streamlit.app'); // Or your actual API endpoint
  gameData = await res.json();

  document.getElementById("origin-name").innerText = gameData.origin_name;
  document.getElementById("origin-svg").src = `https://dashboard-assets.teuteuf.fr/data/common/country-shapes/${gameData.origin_code}.svg`;
}

function handleGuess() {
  if (guessed) return;

  const input = document.getElementById("guess-input");
  const guess = input.value.trim().toLowerCase();
  input.value = "";

  if (gameData.correct_codes.includes(guess)) {
    guessed = true;
    showSuccessPopup();
  } else {
    guessCount++;
    logWrongGuess(guess);
    // TODO: turf projection of guess's antipode cluster
  }
}

function showSuccessPopup() {
  const msg = `🎉 Correct in ${guessCount} guesses!`;
  const popup = document.getElementById("result-popup");
  popup.innerText = msg;
  popup.classList.remove("hidden");
  popup.style.display = "block";
  setTimeout(() => {
    popup.style.display = "none";
  }, 5000);
}

function logWrongGuess(name) {
  const li = document.createElement("li");
  li.innerText = `❌ ${name}`;
  document.getElementById("guess-history").appendChild(li);
}

document.getElementById("submit-guess").addEventListener("click", handleGuess);
window.onload = loadGameData;
