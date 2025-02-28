# MTConnect

## PLC 자료

### 기본 정보
```   
LS Electric 
Model명: XGB-XBC-DR20E   
Software: https://sol.ls-electric.com/ww/en/product/category/477?utm_source=lsehomepage&utm_medium=display&utm_campaign=lse_ww_plc_prod
Online Settings: Connection settings 설정(RS-232C / 포트 COM 확인)
PLC 프로그램 작성 -> STOP모드에서 쓰기 실행 / 읽기 실행
Switch(P0001) -> INC -> D1000 설정 -> Device Monitor 확인 완료

*Modbus 통신 에러 확인 프로그램*
1. Modbus의 경우 프로그램 modpoll 이용: 사이트 https://www.modbusdriver.com/
2. 다운로드 -> cmd -> .exe 경로 -> modpoll -h
3. OR 카페 출처 프로그램 CNET사용   
```   

### 통신 코드    
-----   Windows Version   -----    
통신 모드: Modbus RTU Server (Data 바이너리 형식)
(ASCII 데이터 코드 형식 가능)
(P2P는 PLC끼리 통신, XGT는 XGT 시리즈의 LS 전용 프로토콜)
   
```   
In Python: PLC_Pymodbus.py
1. 필수 모드 설치: pip install pymodbus pyserial
2. Modbus RTU 설정

참고 사이트:
1. PyModBus: https://pymodbus.readthedocs.io/en/latest/source/client.html
2. https://fortex66.tistory.com/13
3. https://lubly0104.tistory.com/10   
```   
- - -

```   
In C#: Program.cs   
1. 프로젝트 생성 (Template: C# Console App (.NET Core) 또는 **C# Console App (.NET Framework))
2. Program.cs 수정
3. 패키지 없을 경우
      ex) NModbus4
         1. Tools -> Nuget Package Manager
         2. Manage Nuget package for solution -> Browse
4. SerialPort 없을 경우
       1. View -> Terminal
       2. 프로젝트 경로로 이동 (csproj 있는 위치)
       3. dotnet add package System.IO.Ports

참고 사이트:
1. PLC 대표 블로그 = https://cafe.naver.com/developautomation
2. https://m.blog.naver.com/PostView.naver?blogId=js__daybyday&logNo=222963701800&navType=by   
```
   
```   
-----   Linux Version   -----
Linux USB 통신 확인: dmesg (pl2303 converter->ttyUSB0)
Linux Modbus 통신용 필수 패키지 설:
      sudo apt update
      sudo apt install -y python3-pip
      pip install pymodbus
      +RTU용
      sudo apt install -y python3-serial
      pip install pymodbus

RTU 통신 확인 방법:
modbus-cli 설치: pip install modbus-cli

📌 Modbus RTU에서 10개의 레지스터 값 읽기
modbus read /dev/ttyUSB0 0 10 --serial
📌 PLC에 값 쓰기 (5번 레지스터에 1234 저장)
modbus write 192.168.1.100 5 1234 --tcp

```

### Agent Build 방법 
```
Windows & Linux
Release(Pre-built & Source): https://github.com/TrakHound/MTConnect.NET/releases/tag/v6.6.0

Build method: https://github.com/mtconnect/cppagent?tab=readme-ov-file  

For windows:

기본-Python3 설치
1. Visual studio에서 C++ 개발 환경이 필요: 설치 시 C++ CMake Tools for Windows 및 MSVC v142 이상이 설치 확인
2. Conan / Ruby / Git 설치
3. cmd -> pip install --upgrade pip -> pip install conan
4. 경로로 이동 후 Agent 다운받기: git clone https://github.com/mtconnect/cppagent.git
5. Environment Setup(개발 도구나 컴파일러가 제대로 작동할 수 있도록 환경 변수와 경로 등을 설정):
   "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
   "C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
6. 해당 경로에서 Conan default 생성: conan profile detect
7. conan create cppagent -pr cppagent/conan/profiles/vs64 --build=missing -o cpack=True -o cpack_destination=C:\Users\smsla\Documents\.

+수동 빌드용 (CMAKE)
빌드용 툴(프로그램) 위치:  C:\Users\jj22j\tools\
Error Solution list (Windows)
1. Error with Cmake and boost Could NOT find Boost (missing: program_options) :
   https://sourceforge.net/projects/boost/files/boost-binaries/1.78.0/

2. Could+NOT+find+LibXml2 : https://pages.lip6.fr/Jean-Francois.Perrot/XML-Int/Session1/WinLibxml.html 
  => CMAKE시 Enviornments Path에 추가 OR Error 뜨는 항목에 PATH 수동 추가 (이방법은 맨 위 Path만 추가하면 됨)
----------------------------------------------------------------------------------------------------------------------------------------------------------------

For Linux:

정석: (현재 cmake시 date_config 오류 발생함)
1. 필수 패키지 설치: sudo apt update / sudo apt install -y cmake g++ make git libboost-all-dev
2. Source 다운로드: git clone https://github.com/mtconnect/cppagent.git -> cd cppagent 이동
3. CMAKE이용 빌드: mkdir build / cd build
      -> cmake .. (빌드)
            이때 자동 다운한 cmake 버전이 낮은 상황이 많음 -> Cmake는 직접 수동으로 다운받아 업데이트해야함 = https://cmake.org/download/
            1. tar -svf 'file'
            2. 해제한 파일로 이동 후, ./bootstrap
                  -> [Error] 'Could not find OpenSSL' -> 해결방법: apt-get install libssl-dev or sudo apt install wget build-essential openssl
                  -> [Error] 'CMake Error at CMakeLists.txt:77 (configure_file): configure_file Problem configuring file' -> 해결방법: Cmake Release 버전 아래로 다시 진행
            3. make
            4. sudo make install
            5. 버전 확인: cmake --version
            + Cmake 다시 설치할 때 (제거): sudo apt purge cmake -> sudo apt autoremove

            Could not find LibXml2: sudo apt-get install libxml2-dev
            Could not find package configuration provided by "date" with any of the following names: dataConfig.cmake date-config.cmake
      -> make -j$(nproc) /

대안: (Conan 사용)
1. sudo apt install -y build-essential cmake gcc-11 g++-11 python3 python3-pip autoconf automake ruby ruby rake 
      python3 -m pip install conan
      echo 'export PATH=$HOME/.local/bin:$PATH' >> .bashrc
2. git clone https://github.com/mtconnect/cppagent.git
3. conan create cppagent -pr cppagent/conan/profiles/gcc --build=missing (cppagent있는 directory에서)
      -> [Error] Default build profile: cd cppagent -> conan profile detect

4. 실행 파일 생성 후 ./agent
5. 빌드가 완료된 후 agent.cfg 파일을 수정하여 MTConnect Agent를 실행: ./agent -c agent.cfg
6. agent.cfg 내에서 수
      Devices = devices.xml
      Adapters = adapter.cfg
      Port = 5000

```

### Agent 실행 방법  
```
Windows
1. Agent 폴더로 이동
2. agent.exe 실행 (명령어 info 나오는거 활용. ex) agent.exe run)
3. Directory: C:\Users\jj22j\JSW_Agent

Linux
1. Agent 폴더로 이동
2. ./agent -c agent.cfg

*웹 브라우저에서 데이터 확인
   - MTConnect Agent가 5000 포트에서 실행되면 http://localhost:5000으로 접속
   - http://localhost:5000/sample → 실시간 데이터 확인
   - http://localhost:5000/current → 현재 데이터 확인


IP 설정
1. 같은 컴퓨터에서 Adapter가 실행될 경우: 로컬 호스트 사용
   -> cmd -> ipconfig
2. 특정 네트워크에서 실행 중이라면 해당 컴퓨터의 IP 주소 입력

Port설정
Adapter의 기본 포트는 MTConnect 표준에서 자주 7878로 사용됨. (Adapter가 설정된 포트 번호와 일치하면 됨)
PLC 포트: 5000

```   

### Programs & Tools needed
```   

https://rubyinstaller.org/ : Ruby+Devkit 3.3.7-1 (x64) 

Alternative method: https://www.trakhound.com/site/  
   => MTConnect.NET (.NET Applications & Tools for MTConnect)
   => Github: https://github.com/TrakHound/MTConnect.NET/tree/master/agent/MTConnect.NET-Agent

```   


