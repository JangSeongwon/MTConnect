# MTConnect

```   
PLC 자료

LS Electric 
Model명: XGB-XBC-DR20E   
Software: https://sol.ls-electric.com/ww/en/product/category/477?utm_source=lsehomepage&utm_medium=display&utm_campaign=lse_ww_plc_prod

현재 통신 방법: Modbus RTU (직렬 통신(RS-232, RS-485) 기반)

Linux Modbus 통신용 필수 패키지 설:
      sudo apt update
      sudo apt install -y python3-pip
      pip install pymodbus
      +RTU용
      sudo apt install -y python3-serial
      pip install pymodbus

```

Agent Build
```
Windows & Linux
Release(Pre-built & Source): https://github.com/TrakHound/MTConnect.NET/releases/tag/v6.6.0

Build method: https://github.com/mtconnect/cppagent?tab=readme-ov-file  

For windows:
1. Visual studio에서 C++ 개발 환경이 필요: 설치 시 C++ CMake Tools for Windows 및 MSVC v142 이상이 설치 확인
CMAKE

For Linux:

1. 필수 패키지 설치: sudo apt update / sudo apt install -y cmake g++ make git libboost-all-dev
2. Source 다운로드: git clone https://github.com/mtconnect/cppagent.git -> cd cppagent 이동
3. CMAKE이용 빌드: mkdir build / cd build / cmake .. (빌드) / make -j$(nproc) / 실행 파일 생성 후 ./agent
4. 빌드가 완료된 후 agent.cfg 파일을 수정하여 MTConnect Agent를 실행: ./agent -c agent.cfg
5. agent.cfg 내에서 수
      Devices = devices.xml
      Adapters = adapter.cfg
      Port = 5000

Agent Run:
1. 에이전트 실행: ./agent -c agent.cfg
2. 웹 브라우저에서 데이터 확인
      MTConnect Agent가 5000 포트에서 실행되면 http://localhost:5000으로 접속
      http://localhost:5000/sample → 실시간 데이터 확인
      http://localhost:5000/current → 현재 데이터 확인


```   

Programs & Tools needed
```   

https://rubyinstaller.org/ : Ruby+Devkit 3.3.7-1 (x64) 

Alternative method: https://www.trakhound.com/site/  
   => MTConnect.NET (.NET Applications & Tools for MTConnect)
   => Github: https://github.com/TrakHound/MTConnect.NET/tree/master/agent/MTConnect.NET-Agent

```   


