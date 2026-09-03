# Local Video Transcriber Project Rules

Always read `/AGENTS.md` before implementing project changes.

The documents under `/docs` define the MVP requirements.

When implementing:

1. Do not expand product scope.
2. Do not introduce cloud infrastructure.
3. Do not introduce a database.
4. Do not implement frontend code.
5. Keep the project a local Python CLI.
6. Large-file reliability is a primary requirement.
7. Processing must be resumable.
8. Do not load complete media into memory.
9. Write tests for non-trivial behavior.
10. Run tests and lint before declaring work complete.

When an architectural choice is not explicitly specified:

prefer:

simple
> explicit
> testable
> reliable

over:

clever
> abstract
> distributed
> overengineered

Never change documented product requirements merely to make implementation easier.

If implementation requires deviating from the documented architecture, document the reason before making the change.
