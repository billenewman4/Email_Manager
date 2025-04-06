# Email Manager

## Overview
Email Manager is an AI-powered system designed to automatically generate personalized, professional emails for networking, job applications, and business communications. Using advanced language models and a multi-agent architecture, the system crafts contextually appropriate emails based on user information, recipient details, and relevant search data.

## System Architecture

### Core Components

#### 1. Agent-Based Architecture
The system implements a sophisticated multi-agent workflow using LangGraph:

- **Supervisor Agent**: Coordinates the overall email generation process and determines workflow routing.
- **Search Agent**: Gathers relevant information about the recipient and their company to inform email content.
- **Drafting Agent**: Creates professional email drafts tailored to specific contexts and user preferences.

#### 2. State Management
The system uses TypedDict-based state management to maintain context throughout the email generation process:
- `EmailState`: Contains critical information like contact details, sender context, draft content, and search results.
- State flows between agents in a directed graph with conditional routing.

#### 3. API Interface
- Built with FastAPI to provide RESTful endpoints
- Supports both single email generation and batch processing
- CORS-enabled for frontend integration

## Workflow Process

1. **Initialization**: The system takes input data including user information (resume, career interests, accomplishments) and contact details.
2. **Information Gathering**: The Search Agent collects and processes relevant information about the contact and their company.
3. **Draft Creation**: The Drafting Agent generates an email using:
   - Contact information
   - User context
   - Search results
   - Optional email templates
4. **Evaluation & Refinement**: The Supervisor Agent reviews the draft and decides whether to:
   - Gather more information (return to Search Agent)
   - Redraft the email (return to Drafting Agent)
   - Finalize the email (end the process)

## API Endpoints

### Single Email Generation
```
POST /generate-email/student
```
Generates a single email based on user and contact information.

### Batch Email Generation
```
POST /generate-email/student/batch
```
Generates multiple emails for an array of contacts using the same user information.

## Configuration

### Environment Variables
The system uses a `.env` file for configuration and API keys.

### Customization Options
- Email templates
- Maximum search attempts
- Maximum redraft attempts
- LLM parameters (temperature, model)

## Technical Implementation

### Language Models
- Uses OpenAI GPT models via LangChain integration
- Updated to use `langchain_openai` imports

### State Management
- Uses TypedDict for state management
- Recent update: Changed `sender` type from Sender object to string context in EmailState

### Agent Communication
- Agents communicate through a shared state object
- Workers track execution order with the `workers_called` list

### Search Mechanism
- Performs targeted searches for information about contacts and companies
- Summarizes results to provide context for email drafting

## Use Cases

1. **Job Seekers**: Generate personalized outreach emails to potential employers or networking contacts
2. **Recruiters**: Create customized messages to candidates
3. **Business Development**: Draft professional emails for partnership opportunities
4. **Sales Outreach**: Personalize communication with potential clients

## Testing
The codebase includes test endpoints to validate functionality:
- `/test` - General system health check
- Custom test functions for various components

## Deployment
The system includes:
- Dockerfile for containerization
- Google Cloud integration (.gcloudignore)
- CORS configuration for production deployment

## Recent Updates
- Changed sender type from Sender object to string context in EmailState and SearchState
- Updated ChatOpenAI imports to use langchain_openai instead of deprecated imports
- Added required email parameter to Sender initialization
- Set default user_type as "student" for email graph creation in test mode
- Updated search agent to handle sender_context as string instead of Sender object

## Requirements
See `requirements.txt` for a complete list of dependencies. Key components include:
- FastAPI
- Uvicorn
- LangChain & LangGraph
- OpenAI
