using System;
using Nova.Core;
using Nova.Simulation;

namespace Nova.SimRunner
{
    internal class ConsoleLogger : INovaLogger
    {
        public bool IsEnabled(LogLevel level) => true;

        public void Log(LogLevel level, string message)
        {
            Console.WriteLine($"[{level}] {message}");
        }

        public void LogTrace(string message) => Log(LogLevel.Trace, message);
        public void LogDebug(string message) => Log(LogLevel.Debug, message);
        public void LogInfo(string message) => Log(LogLevel.Info, message);
        public void LogWarn(string message) => Log(LogLevel.Warn, message);
        public void LogError(string message) => Log(LogLevel.Error, message);
    }

    internal static class Program
    {
        private static void Main(string[] args)
        {
            Console.WriteLine("=== Project Nova - Headless SimRunner ===");

            const ulong seed = 0xAE70123456789000UL;
            var logger = new ConsoleLogger();
            var random = new SimRandom(seed);
            var kernel = new SimulationKernel(random, logger);

            kernel.Start();

            Console.WriteLine($"Running 100 simulation ticks with seed 0x{seed:X}...");
            for (int i = 0; i < 100; i++)
            {
                kernel.StepTick();
            }

            ulong finalHash = kernel.CalculateStateHash();
            Console.WriteLine($"[Success] Simulation reached {kernel.CurrentTick}. Final Hash = 0x{finalHash:X16}");

            kernel.Stop();
        }
    }
}
