const passwordInput = document.getElementById('login-password');
const passwordToggle = document.querySelector('.login-password-toggle');

if (passwordInput && passwordToggle) {
  passwordToggle.addEventListener('click', () => {
    const visible = passwordInput.type === 'password';
    passwordInput.type = visible ? 'text' : 'password';
    passwordToggle.setAttribute('aria-label', visible ? '隐藏密码' : '显示密码');
    passwordToggle.setAttribute('aria-pressed', String(visible));
  });
}
