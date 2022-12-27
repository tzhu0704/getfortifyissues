# 获取FORTIFY SSC数据
本项目对Fortify SSC Restful接口做了封装，支持基于Restful调用接口，定时获取特定状态的Fortify SSC中的漏洞信息，并支持于对应的工具集成，包括：

```集成工具
ServiceNow
SMAX
JIRA
MF ALM
```

## Fortify SSC Restful接口-基于FLASK
```Restful调用方式
print("Hello, World!")
print("Hello, World。。。。。。。。。。。。。。。。。")
```

## 配置文件 config.ini
```config.ini
serverurl=http://10.0.0.118:8080  ##对应的Fortify SSC端口
token=ZTAwNmZkMGEtNTE2Ny00YjE0LWFlYTctY2JmMWQ3MjM5ZWNl ##访问Fortify token
primaryTag=Exploitable#None ##访问Fortify SSC标签
friority=Critical#None ##访问Fortify Vue优先级
severity=2 ##访问严重级别
listenport=8081 ##Flask端口
```