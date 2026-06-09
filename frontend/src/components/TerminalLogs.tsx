import React, { useEffect, useRef, memo } from "react";

interface LogEntry {
  timestamp: string;
  level: "INFO" | "WARNING" | "ERROR" | "SUCCESS";
  message: string;
}

interface TerminalLogsProps {
  logs: LogEntry[];
  title?: string;
}

export const TerminalLogs: React.FC<TerminalLogsProps> = ({ logs, title = "[ TERMINAL DE LOGS ]" }) => {
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const getLevelColor = (level: string): string => {
    switch (level) {
      case "INFO":
        return "text-green-400";
      case "WARNING":
        return "text-yellow-400";
      case "ERROR":
        return "text-red-400";
      case "SUCCESS":
        return "text-blue-400";
      default:
        return "text-green-400";
    }
  };

  return (
    <div className="border border-green-500 p-3 mb-3 bg-black">
      <div className="text-green-400 font-bold mb-2 text-sm">{title}</div>
      <div
        ref={terminalRef}
        className="bg-black border border-green-900 p-2 h-[150px] overflow-y-auto font-mono text-xs"
      >
        {logs.length === 0 ? (
          <div className="text-gray-500">Aguardando logs...</div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="mb-0.5">
              <span className="text-gray-500">[{log.timestamp}]</span>{" "}
              <span className={getLevelColor(log.level)}>[{log.level}]</span>{" "}
              <span className="text-green-300">{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export const TerminalLogsMemo = memo(TerminalLogs);
