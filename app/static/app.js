const dialog = document.querySelector('#idea-dialog');
document.querySelector('#add-idea-btn')?.addEventListener('click', () => dialog.showModal());
document.querySelector('#empty-add')?.addEventListener('click', () => dialog.showModal());
document.querySelector('#close-dialog')?.addEventListener('click', () => dialog.close());
document.querySelector('#cancel-dialog')?.addEventListener('click', () => dialog.close());

const chart = document.querySelector('#views-chart');
if (chart) {
  const series = JSON.parse(chart.dataset.series || '[]');
  const values = series.map(item => Number(item.views));
  const max = Math.max(...values, 1) * 1.15;
  const points = values.map((value, index) => {
    const x = values.length < 2 ? 350 : 12 + index * (676 / (values.length - 1));
    const y = 190 - (value / max) * 180;
    return [x, y];
  });
  const line = points.map((p, i) => `${i ? 'L' : 'M'} ${p[0]} ${p[1]}`).join(' ');
  chart.querySelector('.line-path').setAttribute('d', line);
  chart.querySelector('.area-path').setAttribute('d', `${line} L ${points.at(-1)?.[0] || 688} 205 L ${points[0]?.[0] || 12} 205 Z`);
  chart.querySelector('.x-labels').innerHTML = series.map(item => `<span>${item.day}</span>`).join('');
}
