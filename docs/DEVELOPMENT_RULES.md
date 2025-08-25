# Development Rules & Guidelines

## Project Structure Rules

### 1. Testing Organization
- **All tests must be placed in `tests/` directory**
- Maintain the same directory structure as source code within tests/
- Use descriptive test file names with camelCase (e.g., `testTradingStrategies.py`, `testChartComponents.tsx`)
- Organize tests by feature/module for better maintainability

### 2. Documentation Organization  
- **Only `README.md` should exist in the project root**
- **All other markdown files must be in `docs/` directory**
- Maintain clear documentation hierarchy:
  ```
  docs/
  ├── IMPLEMENTATION_CONTEXT.md    # Development history & context
  ├── TODO.md                      # Implementation roadmap
  ├── API_REFERENCE.md            # API documentation
  ├── DEPLOYMENT_GUIDE.md         # Deployment instructions
  └── Strategies/                 # Strategy analysis documents
  ```

## Naming Convention Rules

### 3.5. CamelCase Standard
- **Use camelCase for all naming conventions** across the entire project
- **Variables**: `currentPrice`, `tradingStrategy`, `riskManagement`
- **Functions**: `calculateMovingAverage()`, `validateTradingSignal()`, `executeOrder()`
- **Files**: `tradingService.py`, `chartComponent.tsx`, `apiClient.js`
- **Database columns**: `createdAt`, `userId`, `portfolioValue`
- **API endpoints**: `/api/getTradingSignals`, `/api/executeOrder`
- **Class names**: Use PascalCase - `TradingStrategy`, `ChartComponent`, `OrderManager`
- **Constants**: Use UPPER_CASE - `MAX_POSITION_SIZE`, `API_TIMEOUT`

### 4. Context Documentation
- **Maintain comprehensive implementation context** in `docs/IMPLEMENTATION_CONTEXT.md`
- Update this document with all major decisions, architectural changes, and rationale
- Include technology choices, trade-offs, and future considerations
- This serves as the **single source of truth** for project evolution and decision history

## Code Organization Rules

### 4. Backend Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API routes
│   ├── core/                   # Core business logic
│   ├── models/                 # Database models
│   ├── services/               # Business services
│   ├── utils/                  # Utility functions
│   └── config.py               # Configuration management
├── requirements.txt            # Python dependencies
└── Dockerfile                  # Container configuration
```

### 5. Frontend Structure
```
frontend/
├── src/
│   ├── components/             # Reusable UI components
│   ├── pages/                  # Page-level components
│   ├── hooks/                  # Custom React hooks
│   ├── services/               # API services
│   ├── store/                  # Redux store configuration
│   ├── types/                  # TypeScript type definitions
│   ├── utils/                  # Utility functions
│   └── App.tsx                 # Main application component
├── package.json                # Node.js dependencies
└── Dockerfile                  # Container configuration
```

## Development Workflow Rules

### 6. Git Commit Standards
- Use conventional commit messages: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Include brief description of changes and rationale
- Reference issue numbers when applicable
- Example: `feat: add candlestick pattern recognition service (#12)`

### 7. Testing Requirements
- **Unit tests** for all business logic functions
- **Integration tests** for API endpoints
- **Component tests** for React components
- **End-to-end tests** for critical user journeys
- Minimum 80% code coverage for production deployments

### 8. Code Quality Standards
- Follow PEP 8 for Python code (with camelCase naming convention)
- Use ESLint and Prettier for TypeScript/JavaScript
- **Use camelCase naming convention** for all variables, functions, and methods across all languages
- Implement type hints in Python
- Use strict TypeScript configuration
- Document all public APIs and complex business logic

## Regulatory & Compliance Rules

### 9. SEBI Compliance Requirements
- **All algorithmic orders must be tagged** with appropriate identifiers
- **Maintain comprehensive audit trails** for all trading decisions
- **Implement kill-switch mechanisms** for emergency stop scenarios
- **Log all user actions** for regulatory review capabilities
- **Ensure data privacy** and secure handling of financial information

### 10. Risk Management Rules
- **Never exceed position limits** defined in configuration
- **Implement circuit breakers** at multiple levels (trade, strategy, portfolio)
- **Validate all trading signals** before execution
- **Maintain real-time risk monitoring** and alerting
- **Require explicit user confirmation** for live trading activation

## Security Rules

### 11. API Security
- **Never store API keys** in source code or configuration files
- **Use environment variables** for sensitive configuration
- **Implement proper authentication** and authorization
- **Validate all inputs** for API endpoints
- **Use HTTPS** for all production communications

### 12. Data Security
- **Encrypt sensitive data** at rest and in transit
- **Implement proper session management**
- **Use secure password policies**
- **Regular security audits** and dependency updates
- **Proper error handling** without exposing internal details

## Performance Rules

### 13. Real-time Data Requirements
- **WebSocket connections** must handle reconnection automatically
- **Data processing latency** must be under 100ms
- **Chart rendering** must maintain 60fps performance
- **Database queries** must be optimized for time-series data
- **Memory usage** must be monitored and controlled

### 14. Scalability Considerations
- **Design for horizontal scaling** from the beginning
- **Use caching strategies** for frequently accessed data
- **Implement proper indexing** for database queries
- **Monitor and profile** performance bottlenecks
- **Plan for data archival** and cleanup strategies

## Monitoring & Observability Rules

### 15. Logging Standards
- **Use structured logging** with consistent format
- **Include request IDs** for tracing across services
- **Log all trading decisions** and their rationale
- **Separate logs by severity** (DEBUG, INFO, WARNING, ERROR)
- **Implement log rotation** and retention policies

### 16. Metrics & Alerting
- **Track business metrics** (trades, P&L, success rates)
- **Monitor technical metrics** (latency, errors, resource usage)
- **Set up alerts** for critical system and business thresholds
- **Create dashboards** for real-time system visibility
- **Regular review** of metrics and alert effectiveness

## Documentation Rules

### 17. Code Documentation
- **Document all public APIs** with clear examples
- **Explain complex business logic** with inline comments
- **Maintain up-to-date README** files for each major component
- **Include architecture diagrams** for system overview
- **Document deployment procedures** and troubleshooting guides

### 18. Decision Documentation
- **Record all architectural decisions** with rationale in IMPLEMENTATION_CONTEXT.md
- **Document trade-offs** and alternative approaches considered
- **Include performance benchmarks** and optimization decisions
- **Maintain changelog** for major feature releases
- **Document known limitations** and future enhancement plans

## Deployment Rules

### 19. Environment Management
- **Separate configurations** for development, staging, and production
- **Use containerization** for consistent deployments
- **Implement proper CI/CD pipelines** with automated testing
- **Maintain infrastructure as code** for reproducible deployments
- **Regular backup procedures** for critical data

### 20. Production Readiness
- **Health checks** for all services
- **Proper error handling** and graceful degradation
- **Resource limits** and monitoring
- **Disaster recovery procedures** documented and tested
- **Security hardening** according to best practices

---

## Context Preservation Rules

### 21. Implementation History
- **Always update IMPLEMENTATION_CONTEXT.md** when making significant changes
- **Include reasoning for technology choices** and architectural decisions  
- **Document lessons learned** and challenges encountered
- **Maintain timeline of major milestones** and deliverables
- **Record performance benchmarks** and optimization results

### 22. Knowledge Transfer
- **Assume future developers** may need complete context
- **Document implicit knowledge** and business domain specifics
- **Include links to external resources** and references used
- **Explain Indian market specifics** and regulatory requirements
- **Maintain glossary** of trading and technical terms

---

**Purpose**: These rules ensure consistent development practices, regulatory compliance, and maintainable codebase for the GoGoTrade AI trading platform.

**Last Updated**: August 25, 2025  
**Review Frequency**: Updated as needed during development, reviewed weekly during active development phases.
