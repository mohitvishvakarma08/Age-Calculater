const form = document.querySelector("#age-form");
let lastResult = null;
const historyKey = "age-calculator-history";

function toIsoDate(value) {
  const match = value.trim().match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
  if (!match) throw new Error("Please use the date format dd/mm/yyyy.");

  const [, day, month, year] = match;
  const date = new Date(Number(year), Number(month) - 1, Number(day));
  if (
    date.getFullYear() !== Number(year) ||
    date.getMonth() !== Number(month) - 1 ||
    date.getDate() !== Number(day)
  ) {
    throw new Error("Please enter a valid date.");
  }

  return `${year}-${month}-${day}`;
}

function validateDateField(field, showIncompleteError = false) {
  const value = field.value.trim();
  field.setCustomValidity("");

  if (!value) return;
  if (!/^\d{2}\/\d{2}\/\d{4}$/.test(value)) {
    if (showIncompleteError) field.setCustomValidity("Use the format dd/mm/yyyy.");
    return;
  }

  try {
    toIsoDate(value);
  } catch (error) {
    field.setCustomValidity(error.message);
  }
}

function formatDate(date) {
  return date.toLocaleDateString("en-GB");
}

function getDownloadName(name) {
  const safeName = name
    .trim()
    .replace(/[<>:"/\\|?*]/g, "")
    .replace(/[. ]+$/, "");
  const displayName = safeName
    ? safeName.charAt(0).toUpperCase() + safeName.slice(1)
    : "User";
  return `${displayName}'s age`;
}

function getHistory() {
  try {
    return JSON.parse(localStorage.getItem(historyKey) || "[]");
  } catch {
    return [];
  }
}

function renderHistory() {
  const historyList = document.querySelector("#history-list");
  const history = getHistory();
  historyList.innerHTML = "";

  if (!history.length) {
    historyList.innerHTML = '<p class="history-empty">Your completed calculations will appear here.</p>';
    return;
  }

  history.forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "history-item";
    row.dataset.historyIndex = index;
    row.tabIndex = 0;
    row.setAttribute("role", "button");
    const name = document.createElement("strong");
    name.textContent = item.name || "User";
    const birth = document.createElement("span");
    birth.textContent = `Born: ${item.birth_date}`;
    const end = document.createElement("span");
    end.textContent = `On: ${item.end_date}`;
    const age = document.createElement("span");
    age.className = "history-age";
    age.textContent = `${item.age_group || "Age group unavailable"} | ${item.age.years} years, ${item.age.months} months, ${item.age.days} days`;
    row.append(name, birth, end, age);
    historyList.appendChild(row);
  });
}

function saveToHistory(result) {
  const history = getHistory();
  history.unshift(result);
  localStorage.setItem(historyKey, JSON.stringify(history.slice(0, 10)));
  renderHistory();
}

function displayResult(result) {
  lastResult = result;
  document.querySelector("#name").value = result.name || "";
  document.querySelector("#birth").value = result.birth_date;
  document.querySelector("#end").value = result.end_date;
  document.querySelector("#result-heading").textContent =
    result.name ? `${result.name}'s age` : "User's age";
  document.querySelector("#years").textContent = result.age.years;
  document.querySelector("#months").textContent = result.age.months;
  document.querySelector("#days").textContent = result.age.days;
  document.querySelector("#age-group").textContent = result.age_group || "—";
  document.querySelector("#born-on").textContent = result.born_on;
  document.querySelector("#next-birthday").textContent = result.next_birthday;
  document.querySelector("#birthday-date").textContent = result.birthday_date;

  for (const [key, value] of Object.entries(result.totals)) {
    document.querySelector(`#total-${key}`).textContent = value.toLocaleString();
  }
}

document.querySelectorAll("#birth, #end").forEach((field) => {
  field.addEventListener("input", () => {
    const digits = field.value.replace(/\D/g, "").slice(0, 8);
    let day = digits.slice(0, 2);
    if (day.length === 2 && Number(day) > 31) day = "31";

    let month = digits.slice(day.length, day.length + 2);
    if (month.length === 2 && Number(month) > 12) month = "12";

    const year = digits.slice(day.length + month.length, day.length + month.length + 4);
    field.value = day;
    if (month || digits.length >= 2) field.value += `/${month}`;
    if (year || digits.length >= 4) field.value += `/${year}`;
    validateDateField(field);
  });

  field.addEventListener("blur", () => validateDateField(field, true));
});

document.querySelectorAll(".calendar-button").forEach((button) => {
  const picker = document.querySelector(`#${button.dataset.picker}`);
  const field = document.querySelector(`#${button.dataset.picker.replace("-picker", "")}`);

  button.addEventListener("click", () => {
    if (field.value.trim()) picker.value = toIsoDate(field.value);
    picker.showPicker();
  });

  picker.addEventListener("change", () => {
    const [year, month, day] = picker.value.split("-");
    field.value = `${day}/${month}/${year}`;
  });
});

document.querySelector("#today").addEventListener("click", () => {
  document.querySelector("#end").value = formatDate(new Date());
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const status = document.querySelector("#status");
  status.textContent = "";

  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: document.querySelector("#name").value,
        birth: toIsoDate(document.querySelector("#birth").value),
        end: toIsoDate(document.querySelector("#end").value),
      }),
    });

    const result = await response.json();
    if (!response.ok) throw new Error(result.error);

    saveToHistory(result);
    displayResult(result);
  } catch (error) {
    status.textContent = error.message || "Could not calculate age.";
  }
});

document.querySelector("#save").addEventListener("click", async () => {
  const status = document.querySelector("#status");
  if (!lastResult) {
    status.textContent = "Calculate the age before saving.";
    return;
  }

  status.textContent = "";
  try {
    const response = await fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...lastResult,
        type: document.querySelector("#export-type").value,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${getDownloadName(lastResult.name)}.${document.querySelector("#export-type").value}`;
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    status.textContent = error.message || "Could not save the file.";
  }
});

document.querySelector("#clear").addEventListener("click", () => {
  lastResult = null;
  document.querySelector("#result-heading").textContent = "User's age";
  document.querySelectorAll(".result-card strong").forEach((item) => {
    item.textContent = "—";
  });
  document.querySelector("#age-group").textContent = "—";
  document.querySelector("#status").textContent = "";
});

document.querySelector("#clear-history").addEventListener("click", () => {
  localStorage.removeItem(historyKey);
  renderHistory();
});

document.querySelector("#history-list").addEventListener("click", (event) => {
  const item = event.target.closest("[data-history-index]");
  if (!item) return;
  displayResult(getHistory()[Number(item.dataset.historyIndex)]);
  document.querySelector("#result-heading").scrollIntoView({ behavior: "smooth", block: "center" });
});

document.querySelector("#history-list").addEventListener("keydown", (event) => {
  if (event.key !== "Enter" && event.key !== " ") return;
  event.preventDefault();
  event.target.click();
});

renderHistory();