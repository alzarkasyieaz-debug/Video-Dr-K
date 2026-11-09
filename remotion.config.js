import {Config} from '@remotion/cli/config';
import fs from 'node:fs';

// Cloud sessions can't download Remotion's headless browser, so use the
// preinstalled Chromium when it exists. Elsewhere Remotion uses its default.
const preinstalled = '/opt/pw-browsers/chromium';
if (fs.existsSync(preinstalled)) {
  Config.setBrowserExecutable(preinstalled);
}
