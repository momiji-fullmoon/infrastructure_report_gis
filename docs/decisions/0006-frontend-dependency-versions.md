# 0006 Frontend dependency versions

The frontend keeps `next` and `eslint-config-next` on the same release line (`16.2.10`) and uses the matching React 19 package line already declared by PR #4. Public npm metadata indicates `eslint-config-next` latest is `16.2.10`, matching the application framework version.

The dependency lockfile must not be edited by hand. Required regeneration procedure:

```bash
cd apps/web
rm -rf node_modules package-lock.json
npm cache verify
npm install
npm ci
npm ls --depth=0
npm run typecheck
npm run lint
npm run build
git diff --exit-code package-lock.json
```

If the npm registry rejects access, do not treat that as success; rerun in an environment that can access `registry.npmjs.org` and commit the generated lockfile.
