// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();

// Элементы DOM
const purchaseOptions = document.querySelectorAll('.purchase-option');
const purchaseBtn = document.getElementById('purchaseBtn');
const notification = document.getElementById('notification');

// Переменные состояния
let selectedOption = null;

// Обработчики выбора варианта покупки
purchaseOptions.forEach(option => {
    option.addEventListener('click', () => {
        // Снимаем выделение со всех вариантов
        purchaseOptions.forEach(opt => opt.classList.remove('selected'));

        // Выделяем выбранный вариант
        option.classList.add('selected');

        // Сохраняем выбранный вариант
        selectedOption = option;

        // Активируем кнопку покупки
        purchaseBtn.disabled = false;
    });
});

// Обработчик нажатия кнопки покупки
purchaseBtn.addEventListener('click', () => {
    if (!selectedOption) return;

    // Получаем данные о выбранной покупке
    const amount = selectedOption.getAttribute('data-amount');
    const price = selectedOption.getAttribute('data-price');

    // Формируем данные для отправки в бота
    const purchaseData = {
        amount: amount,
        price: price,
        currency: 'XTR',
        item: `${amount} SKM`
    };

    // Отправляем данные в бота через WebApp
    try {
        // В реальном приложении здесь будет отправка данных
        tg.sendData(JSON.stringify(purchaseData));

        // Показываем уведомление об успехе
        showNotification('Данные отправлены. Бот отправит счет для оплаты.', 'success');

        // Блокируем кнопку на время обработки
        purchaseBtn.disabled = true;

        // Через 2 секунды закрываем приложение
        setTimeout(() => {
            tg.close();
        }, 2000);

    } catch (error) {
        console.error('Ошибка при отправке данных:', error);
        showNotification('Произошла ошибка. Попробуйте еще раз.', 'error');
    }
});

// Функция показа уведомления
function showNotification(message, type) {
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';

    // Скрываем уведомление через 3 секунды
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Обработчик события, когда бот отправляет данные в веб-приложение
tg.onEvent('viewportChanged', (event) => {
    console.log('Viewport changed:', event);
});

// Инициализация приложения
tg.ready();