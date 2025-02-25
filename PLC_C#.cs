using System;
using System.IO.Ports;
using System.Security.Cryptography.X509Certificates;
using Modbus.Device; // NModbus4 네임스페이스
using XIMUTILLib;

namespace ModbusRtuExample
{
    class Program
    {
        static void Main(string[] args)
        {

            // 시리얼 포트 설정
            using (SerialPort port = new SerialPort("COM5"))
            {
                // PLC의 통신 설정과 일치하도록 설정
                port.BaudRate = 19200;   // PLC의 Baud rate로 설정
                port.Parity = Parity.None; // Parity (PLC와 동일)
                port.DataBits = 8;        // Data bits
                port.StopBits = StopBits.One; // Stop bits
                port.ReadTimeout = 2000;
                port.WriteTimeout = 2000;

                try
                {
                    port.Open();
                    Console.WriteLine("Port Open");
                }
                catch (Exception ex)
                {
                    Console.WriteLine("포트 열기 실패: " + ex.Message);
                    return;
                }




                // Modbus RTU 마스터 생성
                IModbusMaster master = ModbusSerialMaster.CreateRtu(port);

                // Slave ID 설정 (PLC의 Slave ID; 여기서는 1로 가정)
                byte slaveId = 1;

                // PLC의 D0100에 해당하는 Modbus 주소 (예: 0-based로 100)
                ushort startAddress = 100;
                ushort numRegisters = 1;

                try
                {
                    // 레지스터 읽기: D0100의 값을 읽음
                    ushort[] readRegisters = master.ReadHoldingRegisters(slaveId, startAddress, numRegisters);
                    Console.WriteLine("D0100 읽은 값: " + readRegisters[0]);

                    // 레지스터 쓰기: D0100에 값 333 저장
                    ushort writeValue = 333;
                    master.WriteSingleRegister(slaveId, startAddress, writeValue);
                    Console.WriteLine("D0100에 {0} 쓰기 완료", writeValue);
                }
                catch (Exception ex)
                {
                    Console.WriteLine("Modbus 통신 오류: " + ex.Message);
                }
                finally
                {
                    port.Close();
                }
            }
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
        }
    }
}
