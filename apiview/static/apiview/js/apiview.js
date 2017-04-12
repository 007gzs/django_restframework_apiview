var apiview = {
    webSocketBridge:new channels.WebSocketBridge(),
    listenerList:{},
    common_listener:null,
    gen_reqid:function(){
        return "apiview_" + Math.random();
    }
    init:function(options, ws_path){
        self.ws_path = path;
        this.webSocketBridge.connect(path);
        this.webSocketBridge.listen(function(data, stream) {
            var reqid = data['reqid'];
            if(reqid === undefined){
                if (typeof apiview.common_listener === "function") {
                    apiview.common_listener(data);
                }
                return;
            }
            var listener = apiview.listenerList[reqid];
            delete apiview.listenerList[reqid];
            if(!!listener){
                if (data["status_code"] == 200 && typeof listener.success === "function") {
                    listener.success(data["data"]);
                }
                if (typeof listener.error === "function") {
                    listener.error(data, data["status_code"]);
                }
            }
        });
    },
    conn:function(url, data, listener){
        var reqid = this.gen_reqid();
        while(hasOwnProperty(reqid)){
            reqid = this.gen_reqid();
        }
        listenerList[reqid] = listener;
        var req = {path:url, reqid:reqid, data:data};
        this.webSocketBridge.send(req);
    }
};
