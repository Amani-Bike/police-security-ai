const { exec } = require('child_process');
const os = require('os');

function openBrowser() {
  let startCommand;

  switch (os.platform()) {
    case 'darwin': // macOS
      startCommand = 'open';
      break;
    case 'win32': // Windows
      startCommand = 'start';
      break;
    case 'linux': // Linux
      startCommand = 'xdg-open';
      break;
    default:
      console.log('Unsupported platform, cannot open browser automatically');
      return;
  }

  // Wait a moment for the server to start
  setTimeout(() => {
    console.log('Opening browser...');
    exec(`${startCommand} http://localhost:8000`);
  }, 3000);
}

// Open browser when this script is run
openBrowser();

module.exports = { openBrowser };