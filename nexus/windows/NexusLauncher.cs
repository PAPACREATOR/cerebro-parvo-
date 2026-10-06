using System;
using System.Diagnostics;
using System.IO;
using System.Linq;

internal static class NexusLauncher
{
    private static string Quote(string value)
    {
        if (value == null) return "\"\"";
        if (value.Length > 0 && !value.Any(char.IsWhiteSpace) && !value.Contains("\"")) return value;
        return "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
    }

    private static string FindRepoRoot()
    {
        var current = new DirectoryInfo(AppDomain.CurrentDomain.BaseDirectory);
        for (var i = 0; i < 6 && current != null; i++, current = current.Parent)
        {
            var app = Path.Combine(current.FullName, "nexus", "app.py");
            var python = Path.Combine(current.FullName, ".venv", "Scripts", "python.exe");
            if (File.Exists(app) && File.Exists(python))
                return current.FullName;
        }
        throw new FileNotFoundException(
            "Nexus não está preparado. É necessário o repositório e .venv\\Scripts\\python.exe.");
    }

    [STAThread]
    public static int Main(string[] args)
    {
        try
        {
            var root = FindRepoRoot();
            var python = Path.Combine(root, ".venv", "Scripts", "python.exe");
            var forwarded = string.Join(" ", args.Select(Quote));
            var arguments = "-m nexus.app" + (forwarded.Length == 0 ? "" : " " + forwarded);

            var start = new ProcessStartInfo
            {
                FileName = python,
                Arguments = arguments,
                WorkingDirectory = root,
                UseShellExecute = false,
                CreateNoWindow = false
            };
            using (var process = Process.Start(start))
            {
                if (process == null) throw new InvalidOperationException("Não foi possível iniciar o Nexus.");
                process.WaitForExit();
                return process.ExitCode;
            }
        }
        catch (Exception error)
        {
            Console.Error.WriteLine("NEXUS LAUNCHER = FAIL");
            Console.Error.WriteLine(error.Message);
            return 1;
        }
    }
}
