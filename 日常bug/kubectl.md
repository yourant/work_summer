pod 时间设置为和宿主机一致

kubectl get nodes 先获取到集群服务器 ip

在yaml 文件中设置 如下 

配置 volumes (卷), 指定宿主机文件夹

配置 volumeMounts(pod中的挂载点), 指定volumes 中的一个挂载到pod上的某个目录

apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: myweb
spec:
  replicas: 2
  template:
    metadata:
      labels:
        app: myweb
    spec:
      containers:
      - name: myweb
        image: harbor/tomcat:8.5-jre8
        volumeMounts:
        - name: host-time
          mountPath: /etc/localtime
        ports:
        - containerPort: 80
      volumes:
      - name: host-time
        hostPath:
          path: /etc/localtime

由于linux服务器 时间本身就可能会和正常网络时间 之间有误差, 所以需要不断校验本地时间和网络时间, 来保证时间的正确


如下

crontab -e

进入定时任务配置文件, 添加定时任务

每天23:30 执行时间同步,  ntpdate time.windows.com

30 23 * * * /usr/sbin/ntpdate time.windows.com

kubectl get pods --all-namespaces

可以获取到实时的日志

kubectl logs -f --tail=20 pod_name

