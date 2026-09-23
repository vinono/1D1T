const button = document.querySelector('#copy-install');
const status = document.querySelector('#copy-status');
button.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(document.querySelector('#install-command').textContent);
    status.textContent = '已复制，粘贴到终端即可安装。';
  } catch {
    status.textContent = '请选中上方两行命令，手动复制。';
  }
});
