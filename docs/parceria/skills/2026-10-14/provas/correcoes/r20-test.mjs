import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
const require = createRequire(import.meta.url);
const YAML = require(process.env.CI_YAML_MODULE || 'yaml');
const workflow = YAML.parse(fs.readFileSync(process.argv[2], 'utf8'));
const checks = [];
const ck = (name, pass) => checks.push({ name, pass: !!pass });
const sec = workflow.jobs.security,
  stage = workflow.jobs['deploy-staging'],
  prod = workflow.jobs['deploy-prod'];
const steps = sec.steps,
  scan = steps.find((s) => s.id === 'scan');
const upload = steps.find((s) => s.with?.name === 'scanned-image');
const publish = stage.steps.find((s) => s.id === 'publish');
const stageDeploy = stage.steps.find((s) => s.env?.IMAGE_REF);
const prodDeploy = prod.steps.find((s) => s.env?.IMAGE_REF);
const allRuns = Object.values(workflow.jobs)
  .flatMap((j) => j.steps || [])
  .map((s) => s.run || '')
  .join('\n');
ck(
  'Uma construção Docker, no job de segurança',
  (allRuns.match(/docker build\b/g) || []).length === 1 && !!scan?.run.includes('docker build'),
);
ck(
  'Arquivo do scan só é publicado após sucesso',
  scan &&
    upload &&
    steps.indexOf(upload) > steps.indexOf(scan) &&
    !upload.if &&
    upload.with.path === '${{ runner.temp }}/app-ci.tar' &&
    upload.with['if-no-files-found'] === 'error',
);
ck(
  'Identidades vêm do job de segurança',
  sec.outputs?.['archive-sha'] === '${{ steps.scan.outputs.archive-sha }}' &&
    sec.outputs?.['image-id'] === '${{ steps.scan.outputs.image-id }}' &&
    publish?.env.EXPECTED_ARCHIVE_SHA === '${{ needs.security.outputs.archive-sha }}' &&
    publish?.env.EXPECTED_IMAGE_ID === '${{ needs.security.outputs.image-id }}',
);
ck(
  'Staging recupera o mesmo artefato',
  stage.needs.includes('security') &&
    stage.steps.some(
      (s) => s.with?.name === 'scanned-image' && s.uses?.startsWith('actions/download-artifact@'),
    ),
);
ck(
  'Staging e produção usam exatamente o digest publicado',
  stage.outputs?.['image-ref'] === '${{ steps.publish.outputs.image-ref }}' &&
    stageDeploy?.env.IMAGE_REF === '${{ steps.publish.outputs.image-ref }}' &&
    prod.needs === 'deploy-staging' &&
    prodDeploy?.env.IMAGE_REF === '${{ needs.deploy-staging.outputs.image-ref }}' &&
    !/docker build|docker push/.test(prodDeploy?.run || ''),
);
if (publish) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'r20-ci-'));
  try {
    fs.mkdirSync(path.join(root, 'bin'));
    fs.mkdirSync(path.join(root, 'scanned'));
    const tar = path.join(root, 'scanned/app-ci.tar');
    fs.writeFileSync(tar, 'synthetic archive\n');
    const sha = spawnSync('shasum', ['-a', '256', tar], { encoding: 'utf8' }).stdout.split(' ')[0];
    const digest = 'sha256:' + 'a'.repeat(64),
      repository = 'registry.example/app';
    fs.writeFileSync(path.join(root, 'bin/sha256sum'), '#!/bin/sh\nexec shasum -a 256 "$@"\n', {
      mode: 0o755,
    });
    fs.writeFileSync(
      path.join(root, 'bin/docker'),
      `#!/bin/bash
printf '%s\\n' "$*" >> "$DOCKER_LOG"
if [[ "$1 $2" == 'image inspect' ]]; then
  if [[ "$*" == *RepoDigests* ]]; then
    if [[ "$CASE" != nodigest ]]; then printf '%s\\n' "$IMAGE_REPOSITORY@$EXPECTED_IMAGE_ID"; fi
  elif [[ "$CASE" == wrongimage && "$3" == app:ci ]] || [[ "$CASE" == wrongremote && "$3" == *@sha256:* ]]; then
    printf 'sha256:%064d\\n' 1
  else printf '%s\\n' "$EXPECTED_IMAGE_ID"; fi
fi
`,
      { mode: 0o755 },
    );
    for (const scenario of ['valid', 'corrupt', 'wrongimage', 'nodigest', 'wrongremote']) {
      const log = path.join(root, 'calls'),
        output = path.join(root, 'output');
      fs.writeFileSync(log, '');
      fs.writeFileSync(output, '');
      const env = {
        ...process.env,
        PATH: path.join(root, 'bin') + ':' + process.env.PATH,
        RUNNER_TEMP: root,
        IMAGE_REPOSITORY: repository,
        EXPECTED_IMAGE_ID: digest,
        EXPECTED_ARCHIVE_SHA: scenario === 'corrupt' ? '0'.repeat(64) : sha,
        GITHUB_SHA: 'b'.repeat(40),
        GITHUB_OUTPUT: output,
        DOCKER_LOG: log,
        CASE: scenario,
      };
      const run = spawnSync('bash', ['-c', publish.run], { env, encoding: 'utf8' });
      const calls = fs.readFileSync(log, 'utf8'),
        out = fs.readFileSync(output, 'utf8');
      ck(
        'Shell publicação simulada: ' + scenario,
        scenario === 'valid'
          ? run.status === 0 && out === `image-ref=${repository}@${digest}\n` && !calls.includes('build')
          : run.status !== 0 &&
              out === '' &&
              (!['corrupt', 'wrongimage'].includes(scenario) || !calls.includes('push')),
      );
    }
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
} else ck('Etapa publicadora executável existe', false);
console.log(JSON.stringify(checks, null, 2));
console.log(`${checks.filter((x) => x.pass).length}/${checks.length}`);
process.exit(checks.every((x) => x.pass) ? 0 : 1);
