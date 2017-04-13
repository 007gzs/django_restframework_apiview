from apiview.consumers import ApiViewConsumer


channel_routing = [
    ApiViewConsumer.as_route(path="^/apiview")
]
