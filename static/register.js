const passwordInput = document.getElementById("register-password");
const passwordHelp = document.getElementById("password-help");
const passwordToggle = document.querySelector(".register-form .login-password-toggle");

if (passwordInput && passwordToggle) {
  passwordToggle.addEventListener("click", () => {
    const visible = passwordInput.type === "password";
    passwordInput.type = visible ? "text" : "password";
    passwordToggle.setAttribute("aria-label", visible ? "隐藏密码" : "显示密码");
    passwordToggle.setAttribute("aria-pressed", String(visible));
  });
}

if (passwordInput && passwordHelp) {
  const checks = {
    length: value => Array.from(value).length >= 8 && Array.from(value).length <= 20,
    lower: value => /[a-z]/.test(value),
    upper: value => /[A-Z]/.test(value),
    digit: value => /[0-9]/.test(value),
    punctuation: value => Array.from(value).some(char => {
      const code = char.charCodeAt(0);
      return (code >= 33 && code <= 47) || (code >= 58 && code <= 64) ||
        (code >= 91 && code <= 96) || (code >= 123 && code <= 126);
    })
  };

  function updatePasswordHelp() {
    let satisfiedCount = 0;
    for (const [name, check] of Object.entries(checks)) {
      const item = passwordHelp.querySelector(`[data-rule="${name}"]`);
      const satisfied = check(passwordInput.value);
      item.classList.toggle("satisfied", satisfied);
      item.querySelector(".rule-icon").textContent = satisfied ? "✓" : "○";
      item.querySelector(".rule-status").textContent = satisfied ? "已满足" : "未满足";
      if (satisfied) satisfiedCount++;
    }
    const progress = document.getElementById("password-progress");
    const message = `已满足 ${satisfiedCount}/5 项`;
    if (progress.textContent !== message) progress.textContent = message;
  }

  passwordInput.addEventListener("focus", () => { passwordHelp.hidden = false; });
  passwordInput.addEventListener("input", updatePasswordHelp);
  passwordInput.addEventListener("blur", () => { passwordHelp.hidden = true; });
  updatePasswordHelp();
}
