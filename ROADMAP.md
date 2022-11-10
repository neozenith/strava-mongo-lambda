# ROADMAP

Glorified TODO list

 - handle refresh tokens
 - add Jinja templates to render the basic website UI
 - Switch from Strava Swagger codegen to raw HTTP requests
 - Handle redirects after login correctly 
   - very tricky when browsers proactively make many calls and we can wind up with duplicate calls mutating cookie states
   - Perhaps only clear redirect once it hits the target route?