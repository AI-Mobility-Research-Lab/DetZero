import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

class DetZeroViewer {
    constructor() {
        this.currentFrame = 0;
        this.isPlaying = false;
        this.playInterval = null;
        
        this.beforeData = [];
        this.afterData = [];
        
        this.sceneBefore = null;
        this.sceneAfter = null;
        this.cameraBefore = null;
        this.cameraAfter = null;
        this.rendererBefore = null;
        this.rendererAfter = null;
        this.controlsBefore = null;
        this.controlsAfter = null;
        
        this.init();
    }
    
    async init() {
        console.log('DetZeroViewer: Starting initialization...');
        try {
            await this.loadData();
            console.log('DetZeroViewer: Data loaded successfully');
            
            // Show container BEFORE setting up scenes so dimensions are available
            document.getElementById('loading').style.display = 'none';
            document.getElementById('container').style.display = 'flex';
            
            // Small delay to ensure layout is calculated
            await new Promise(resolve => setTimeout(resolve, 100));
            
            this.setupScenes();
            console.log('DetZeroViewer: Scenes setup complete');
            
            this.setupControls();
            console.log('DetZeroViewer: Controls setup complete');
            
            this.loadFrame(0);
            console.log('DetZeroViewer: First frame loaded');
            
            this.animate();
            console.log('DetZeroViewer: Animation started, initialization complete!');
        } catch (error) {
            console.error('DetZeroViewer initialization error:', error);
            alert('Failed to initialize visualizer: ' + error.message);
        }
    }
    
    async loadData() {
        try {
            // Load the data files
            const [beforeResponse, afterResponse] = await Promise.all([
                fetch('data/detection_data.json'),
                fetch('data/refined_data.json')
            ]);
            
            this.beforeData = await beforeResponse.json();
            this.afterData = await afterResponse.json();
            
            console.log('Loaded data:', {
                before: this.beforeData.length,
                after: this.afterData.length
            });
            
            // Update slider max
            const maxFrames = Math.min(this.beforeData.length, this.afterData.length);
            document.getElementById('frame-slider').max = maxFrames - 1;
            document.getElementById('current-frame').textContent = `0 / ${maxFrames}`;
            
        } catch (error) {
            console.error('Error loading data:', error);
            alert('Error loading visualization data. Please ensure data files are present.');
        }
    }
    
    setupScenes() {
        console.log('Setting up scenes...');
        
        // Setup Before scene
        this.sceneBefore = new THREE.Scene();
        this.sceneBefore.background = new THREE.Color(0x1a1a2e);
        
        this.cameraBefore = new THREE.PerspectiveCamera(
            60,
            window.innerWidth / 2 / window.innerHeight,
            0.1,
            1000
        );
        this.cameraBefore.position.set(50, 50, 50);
        this.cameraBefore.lookAt(0, 0, 0);
        
        const containerBefore = document.getElementById('canvas-before');
        console.log('Before container dimensions:', containerBefore.clientWidth, 'x', containerBefore.clientHeight);
        
        this.rendererBefore = new THREE.WebGLRenderer({ antialias: true });
        this.rendererBefore.setSize(containerBefore.clientWidth, containerBefore.clientHeight);
        containerBefore.appendChild(this.rendererBefore.domElement);
        
        this.controlsBefore = new OrbitControls(this.cameraBefore, this.rendererBefore.domElement);
        this.controlsBefore.enableDamping = true;
        this.controlsBefore.dampingFactor = 0.05;
        
        // Setup After scene
        this.sceneAfter = new THREE.Scene();
        this.sceneAfter.background = new THREE.Color(0x1a1a2e);
        
        this.cameraAfter = new THREE.PerspectiveCamera(
            60,
            window.innerWidth / 2 / window.innerHeight,
            0.1,
            1000
        );
        this.cameraAfter.position.set(50, 50, 50);
        this.cameraAfter.lookAt(0, 0, 0);
        
        const containerAfter = document.getElementById('canvas-after');
        console.log('After container dimensions:', containerAfter.clientWidth, 'x', containerAfter.clientHeight);
        
        this.rendererAfter = new THREE.WebGLRenderer({ antialias: true });
        this.rendererAfter.setSize(containerAfter.clientWidth, containerAfter.clientHeight);
        containerAfter.appendChild(this.rendererAfter.domElement);
        
        this.controlsAfter = new OrbitControls(this.cameraAfter, this.rendererAfter.domElement);
        this.controlsAfter.enableDamping = true;
        this.controlsAfter.dampingFactor = 0.05;
        
        // Add lights to both scenes
        [this.sceneBefore, this.sceneAfter].forEach(scene => {
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(50, 50, 50);
            scene.add(directionalLight);
            
            // Add ground plane
            const groundGeometry = new THREE.PlaneGeometry(150, 150);
            const groundMaterial = new THREE.MeshStandardMaterial({
                color: 0x2a2a3e,
                side: THREE.DoubleSide
            });
            const ground = new THREE.Mesh(groundGeometry, groundMaterial);
            ground.rotation.x = -Math.PI / 2;
            ground.position.y = -0.1;
            scene.add(ground);
            
            // Add grid
            const gridHelper = new THREE.GridHelper(150, 30, 0x444444, 0x333333);
            scene.add(gridHelper);
            
            // Add axes
            const axesHelper = new THREE.AxesHelper(10);
            scene.add(axesHelper);
        });
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }
    
    setupControls() {
        const frameSlider = document.getElementById('frame-slider');
        const playBtn = document.getElementById('play-btn');
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        const resetViewBtn = document.getElementById('reset-view-btn');
        
        frameSlider.addEventListener('input', (e) => {
            this.currentFrame = parseInt(e.target.value);
            this.loadFrame(this.currentFrame);
        });
        
        playBtn.addEventListener('click', () => this.togglePlay());
        prevBtn.addEventListener('click', () => this.previousFrame());
        nextBtn.addEventListener('click', () => this.nextFrame());
        resetViewBtn.addEventListener('click', () => this.resetView());
    }
    
    loadFrame(frameIndex) {
        if (frameIndex < 0 || frameIndex >= this.beforeData.length) return;
        
        this.currentFrame = frameIndex;
        
        // Clear existing boxes
        this.clearBoxes(this.sceneBefore);
        this.clearBoxes(this.sceneAfter);
        
        // Load before boxes
        const beforeFrame = this.beforeData[frameIndex];
        const afterFrame = this.afterData[frameIndex];
        
        if (beforeFrame && beforeFrame.boxes) {
            beforeFrame.boxes.forEach(box => {
                this.addBox(this.sceneBefore, box);
            });
        }
        
        if (afterFrame && afterFrame.boxes) {
            afterFrame.boxes.forEach(box => {
                this.addBox(this.sceneAfter, box);
            });
        }
        
        // Update UI
        this.updateStats(beforeFrame, afterFrame);
        document.getElementById('frame-slider').value = frameIndex;
        document.getElementById('frame-number').textContent = frameIndex;
        document.getElementById('current-frame').textContent = 
            `${frameIndex} / ${this.beforeData.length}`;
    }
    
    clearBoxes(scene) {
        const objectsToRemove = [];
        scene.traverse((object) => {
            if (object.userData.isBox) {
                objectsToRemove.push(object);
            }
        });
        objectsToRemove.forEach(obj => scene.remove(obj));
    }
    
    addBox(scene, box) {
        const { center, size, rotation, score } = box;
        
        // Create box geometry
        const geometry = new THREE.BoxGeometry(size[0], size[2], size[1]);
        
        // Color based on score
        let color;
        if (score > 0.9) {
            color = 0x00ff00; // Green
        } else if (score > 0.7) {
            color = 0xffff00; // Yellow
        } else {
            color = 0xff0000; // Red
        }
        
        const material = new THREE.MeshStandardMaterial({
            color: color,
            transparent: true,
            opacity: 0.3,
            side: THREE.DoubleSide
        });
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(center[0], center[2], center[1]);
        mesh.rotation.y = rotation;
        
        // Add edges
        const edges = new THREE.EdgesGeometry(geometry);
        const lineMaterial = new THREE.LineBasicMaterial({ color: color, linewidth: 2 });
        const lineSegments = new THREE.LineSegments(edges, lineMaterial);
        mesh.add(lineSegments);
        
        mesh.userData.isBox = true;
        scene.add(mesh);
    }
    
    updateStats(beforeFrame, afterFrame) {
        const beforeBoxes = beforeFrame?.boxes?.length || 0;
        const afterBoxes = afterFrame?.boxes?.length || 0;
        const diff = afterBoxes - beforeBoxes;
        
        const beforeScore = beforeFrame?.boxes?.length > 0 
            ? (beforeFrame.boxes.reduce((sum, b) => sum + b.score, 0) / beforeFrame.boxes.length).toFixed(3)
            : '0.000';
        
        const afterScore = afterFrame?.boxes?.length > 0
            ? (afterFrame.boxes.reduce((sum, b) => sum + b.score, 0) / afterFrame.boxes.length).toFixed(3)
            : '0.000';
        
        document.getElementById('before-boxes').textContent = beforeBoxes;
        document.getElementById('after-boxes').textContent = afterBoxes;
        document.getElementById('box-diff').textContent = diff >= 0 ? `+${diff}` : diff;
        document.getElementById('box-diff').style.color = diff >= 0 ? '#4ade80' : '#f87171';
        document.getElementById('before-score').textContent = beforeScore;
        document.getElementById('after-score').textContent = afterScore;
    }
    
    togglePlay() {
        this.isPlaying = !this.isPlaying;
        const playBtn = document.getElementById('play-btn');
        
        if (this.isPlaying) {
            playBtn.textContent = '⏸️ Pause';
            this.playInterval = setInterval(() => {
                this.nextFrame();
                if (this.currentFrame >= this.beforeData.length - 1) {
                    this.togglePlay();
                }
            }, 200);
        } else {
            playBtn.textContent = '▶️ Play';
            if (this.playInterval) {
                clearInterval(this.playInterval);
                this.playInterval = null;
            }
        }
    }
    
    previousFrame() {
        if (this.currentFrame > 0) {
            this.loadFrame(this.currentFrame - 1);
        }
    }
    
    nextFrame() {
        if (this.currentFrame < this.beforeData.length - 1) {
            this.loadFrame(this.currentFrame + 1);
        }
    }
    
    resetView() {
        this.cameraBefore.position.set(50, 50, 50);
        this.cameraBefore.lookAt(0, 0, 0);
        this.controlsBefore.reset();
        
        this.cameraAfter.position.set(50, 50, 50);
        this.cameraAfter.lookAt(0, 0, 0);
        this.controlsAfter.reset();
    }
    
    onWindowResize() {
        const containerBefore = document.getElementById('canvas-before');
        const containerAfter = document.getElementById('canvas-after');
        
        this.cameraBefore.aspect = containerBefore.clientWidth / containerBefore.clientHeight;
        this.cameraBefore.updateProjectionMatrix();
        this.rendererBefore.setSize(containerBefore.clientWidth, containerBefore.clientHeight);
        
        this.cameraAfter.aspect = containerAfter.clientWidth / containerAfter.clientHeight;
        this.cameraAfter.updateProjectionMatrix();
        this.rendererAfter.setSize(containerAfter.clientWidth, containerAfter.clientHeight);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.controlsBefore.update();
        this.controlsAfter.update();
        
        this.rendererBefore.render(this.sceneBefore, this.cameraBefore);
        this.rendererAfter.render(this.sceneAfter, this.cameraAfter);
    }
}

// Initialize viewer when page loads
window.addEventListener('DOMContentLoaded', () => {
    new DetZeroViewer();
});
