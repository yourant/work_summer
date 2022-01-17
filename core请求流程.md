1. tornado 请求都是通过handler转发， 首先进入 core/service/handlers.py,

调用execute 方法， 


2. 通过主 handlers.py 转发到 子模块的 handlers

