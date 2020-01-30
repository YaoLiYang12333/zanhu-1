$(function () {
    const emptyMessage = '没有未读通知';
    // 调用的是 notification_list.html 中line 15
    const notice = $('#notifications');

    function CheckNotifications() {
        // 检查消息通知
        $.ajax({
            url: '/notifications/latest-notifications/',
            cache: false,
            success: function (data) {
                if (!data.includes(emptyMessage)) {
                    notice.addClass('btn-danger');
                }
            },
        });
    }

    CheckNotifications();  // 页面加载时执行

    // 更新动态 news_single.html line3 news_id = "{{ news.uuid_id }}"
    // 根据id_value (主键id)
    function update_social_activity(id_value) {
        // 选中具体 的某一条动态
        const newsToUpdate = $('[news-id=' + id_value + ']');
        $.ajax({
            url: '/news/update-interactions/',
            data: {'id_value': id_value},
            type: 'POST',
            cache: false,
            success: function (data) {
                $(".like-count", newsToUpdate).text(data.likes);
                $(".comment-count", newsToUpdate).text(data.comments);
            },
        });
    }

    // 点击提醒时 （点击铃铛按钮）
    notice.click(function () {
        // 如果已出现
        if ($('.popover').is(':visible')) {
            notice.popover('hide');
            CheckNotifications(); // 获取最近的通知
        } else {
            notice.popover('dispose');
            // 再次发起ajax请求
            $.ajax({
                url: '/notifications/latest-notifications/',
                cache: false,
                success: function (data) {
                    notice.popover({
                        html: true,
                        trigger: 'focus',
                        container: 'body',
                        placement: 'bottom',
                        content: data,
                    });
                    notice.popover('show');
                    notice.removeClass('btn-danger')
                },
            });
        }
        return false;  // 不是False
    });

    // WebSocket连接，使用wss(https)或者ws(http)
    const ws_scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws_path = ws_scheme + '://' + window.location.host + '/ws/notifications/';
    const ws = new ReconnectingWebSocket(ws_path);

    // 监听后端发送过来的消息
    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        // 在notification_handler 中发给视图的函数，中的key值
        switch (data.key) {
            // 如果key为notification
            case "notification":
                if (currentUser !== data.actor_name) {  // 消息提示的发起者 不等于动作执行者  即提示消息
                    notice.addClass('btn-danger');  // 将消息通知 铃铛按钮 变为警告(红色)
                }
                break;
            // 如果key为social_update 有人点赞
            case "social_update":
                if (currentUser !== data.actor_name) {
                    notice.addClass('btn-danger');
                }
                update_social_activity(data.id_value);  // 触发另外JS 刷新点赞数量
                break;
            // 如果key为social_update 有用户发表新动态
            case "additional_news":
                if (currentUser !== data.actor_name) {
                    // 来自于首页动态 news_list.html line 22  通过类选择器
                    // 当有新动态时，首页显示有动态提示，点击提示，即刷新你页面
                    $('.stream-update').show();
                }
                break;

            default:
                console.log('error', data);
                break;
        }
    };
});
