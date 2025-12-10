// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: ROS2 Foundations',
      items: ['ros2-foundations/index'],
    },
    {
      type: 'category',
      label: 'Module 2: Simulation',
      items: ['simulation/index'],
    },
    {
      type: 'category',
      label: 'Module 3: NVIDIA Isaac',
      items: ['nvidia-isaac/index'],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action (VLA)',
      items: ['vla-humanoids/index'],
    },
  ],
};

module.exports = sidebars;