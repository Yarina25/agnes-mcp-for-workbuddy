@echo off
chcp 65001 >nul
title Agnes MCP Server - 调试模式
echo ============================================
echo   Agnes MCP Server（调试模式）
echo   用途：手动启动服务、查看报错日志
echo   日常使用请关闭本窗口，交给 WorkBuddy 自动拉起
echo ============================================
echo.
cd /d "%~dp0"
python agnes_mcp_server.py
echo.
echo 服务已退出（按任意键关闭窗口）
pause >nul
