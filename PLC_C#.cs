using System;
using System.IO.Ports;
using System.Security.Cryptography.X509Certificates;
using Modbus.Device; // Modbus 네임스페이스
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
                // PLC와 통신 설정값 일치하도록 설정
                port.BaudRate = 38400; // PLC Baud rate 설정
                port.Parity = Parity.None; // Parity (PLC와 동일)
                port.DataBits = 8; // Data bits
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
            }

            // Modbus RTU 마스터 생성
            IModbusMaster master = ModbusSerialMaster.CreateRtu(port);

            // Slave ID 설정 (PLC의 Slave ID, 여기서는 1로 가정)
            byte slaveId = 1;

            // PLC의 D100에 해당하는 Modbus 주소 (예: 0-based로 100)
            ushort startAddress = 40101;
            ushort numRegisters = 1;
        }
    }
}
