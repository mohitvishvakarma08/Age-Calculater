const form = document.querySelector("#age-form");
let lastResult = null;

document.querySelector("#today").addEventListener("click", () => {
  document.querySelector("#end").value = new Date().toISOString().slice(0, 10);
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
        birth: document.querySelector("#birth").value,
        end: document.querySelector("#end").value,
      }),
    });

    const result = await response.json();
    if (!response.ok) throw new Error(result.error);

    lastResult = result;
    document.querySelector("#result-heading").textContent =
      result.name ? `${result.name}'s age` : "Your age";

    document.querySelector("#years").textContent = result.age.years;
    document.querySelector("#months").textContent = result.age.months;
    document.querySelector("#days").textContent = result.age.days;
    document.querySelector("#born-on").textContent = result.born_on;
    document.querySelector("#next-birthday").textContent = result.next_birthday;
    document.querySelector("#birthday-date").textContent = result.birthday_date;

    for (const [key, value] of Object.entries(result.totals)) {
      document.querySelector(`#total-${key}`).textContent = value.toLocaleString();
    }
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
    link.download = `age-calculation.${document.querySelector("#export-type").value}`;
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    status.textContent = error.message || "Could not save the file.";
  }
});

document.querySelector("#clear").addEventListener("click", () => {
  lastResult = null;
  document.querySelector("#result-heading").textContent = "Your age";
  document.querySelectorAll(".result-card strong").forEach((item) => {
    item.textContent = "—";
  });
  document.querySelector("#status").textContent = "";
});