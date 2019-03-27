let csrfmiddlewaretoken = $('#csrfmiddlewaretoken').children()[0].value;
// Отписаться
$('.subscribe_off').click(function () {
    let id = $(this).closest('.entity')[0].id;
    //let subscribe = false;
    $.post('/news/', { id: id, subscribe: false, csrfmiddlewaretoken: csrfmiddlewaretoken }, window.location.reload())
});

// Подписаться
$('.subscribe_on').click(function () {
    let id = $(this).closest('.entity')[0].id;
    $.post('/news/', { id: id, subscribe: true, csrfmiddlewaretoken: csrfmiddlewaretoken }, window.location.reload())
});

// Пометить пост как прочтенный
$('.mark_as_readable').click(function () {
    let post_id = $(this).closest('.entity_header')[0].id;
    $.post('/news/', { post_id: post_id, read: true, csrfmiddlewaretoken: csrfmiddlewaretoken }, window.location.reload())
});

// Получить состояние "прочитанности" и изменить DOM
$.getJSON('/api.main/read/get', { get_read: true }, (data) => {
    for (let item of data['read']) {
        // Можно повесить любое другое отображение "прочитанности"
        $(`div#${item.id}.entity_header`).children('button.mark_as_readable').html('Прочитано');
        }
     })