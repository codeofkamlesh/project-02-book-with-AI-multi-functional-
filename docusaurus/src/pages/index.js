import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Read the Book - 5 min ⏱️
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();

  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="AI/Spec-Driven Robotics Book: A comprehensive guide to humanoid robotics using ROS 2, Simulation, Isaac, and Vision-Language-Action systems">
      <HomepageHeader />
      <main>
        <div className="container">
          <div className="row">
            <div className="col col--6 col--offset-3">
              <h2>Learn Humanoid Robotics</h2>
              <p>
                This comprehensive guide covers the complete pipeline from basic ROS 2 concepts to advanced Vision-Language-Action (VLA) systems for humanoid robot control.
              </p>
              <p>
                Navigate through our structured curriculum covering ROS2 Foundations, Simulation environments, NVIDIA Isaac, and Vision-Language-Action systems.
              </p>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}