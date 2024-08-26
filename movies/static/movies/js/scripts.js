document.addEventListener('DOMContentLoaded', function () {
    var textarea = document.querySelector('textarea[name="text"]');
    var charCountSpan = document.getElementById('char-count');
    var maxLength = 500;
    // Функция для обновления счетчика символов
    function updateCharCount() {
        var remaining = maxLength - textarea.value.length;
        charCountSpan.textContent = remaining;
    }
    // Инициализировать счетчик при загрузке страницы
    updateCharCount();
    textarea.addEventListener('input', updateCharCount);
});