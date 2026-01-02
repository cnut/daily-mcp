# Introduction

This is a simple mcp server to record daily life in LLM way.

# Function

- [ ] only login in local env
- [ ] internal built-in schema, such (finance, health, todo task, daily log)

## login in local env

nowadays, we want to keep the server as simple as possible, so we only support login in local env, this means:
- use local files to store state,
- use embedded database (such as SQLLite) to store data.

## internal built-in schema

## finance

this mcp server will store daily income, cost and the detailed information.

## todo

this mcp server will also support creating or finishing the todo,
during everyday 10:00 or 8:00, the todo message is popped the agent side to remind the user.

## health

this mcp server will record the user's health status, such as blood pressure, blood sugar, heart rate, etc.

## daily log

this mcp server will record the user's daily log, such as what did you eat, what did you do, etc.
this daily log can be used as the raw data of other schema, it's the raw bla bla words inputted by the user from agent side. 
