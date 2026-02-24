import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

class AblationViewer {
    constructor() {
        this.currentFrame = 0;
        this.isPlaying = false;
        this.data = {};
        this.scenes = {};
        this.cameras = {};
        this.renderers = {};
        this.controls = {};
        
        this.types = ['det', 'grm-prm', 'full'];
        this.files = {
            'det': 'detection_data.json',
            'grm-prm': 'grm_prm_data.json',
            'full': 'grm_prm_crm_data.json'
        };
        
        this.init();
    }
    
    async init() {
        try {
            await this.loadData();
            document.getElementById('loading').style.display = 'none';
            document.getElementById('container').style.display = 'flex';
            
            await new Promise(resolve => setTimeout(resolve, 100));
            
            this.setupScenes();
            this.setupControls();
            this.loadFrame(0);
            this.animate();
        } catch (error) {
            console.error('Init error:', error);
            alert('Failed to load: ' + error.message);
        }
    }
    
    async loadData() {
        const promises = this.types.map(async type => {
            const response = await fetch(`data/ablation/${this.files[type]}`);
            this.data[type] = await response.json();
        });
        
        await Promise.all(promises);
        
        const maxFrames = Math.min(...this.types.map(t => this.data[t].length));
        document.getElementById('frame-slider').max = maxFrames - 1;
        document.getElementById('current-frame').textContent = `0 / ${maxFrames}`;
    }
    
    setupScenes() {
        this.types.forEach(type => {
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a2e);
            
            const container = document.getElementById(`canvas-${type}`);
            const camera = new THREE.PerspectiveCamera(60, 
                container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(50, 50, 50);
            camera.lookAt(0, 0, 0);
            
            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);
            
            const controls = new OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            
            // Lights
            scene.add(new THREE.AmbientLight(0xffffff, 0.6));
            const light = new THREE.DirectionalLight(0xffffff, 0.8);
            light.position.set(50, 50, 50);
            scene.add(light);
            
            // Ground
            const ground = new THREE.Mesh(
                new THREE.PlaneGeometry(150, 150),
                new THREE.MeshStandardMaterial({ color: 0x2a2a3e, side: THREE.DoubleSide })
            );
            ground.rotation.x = -Math.PI / 2;
            ground.position.y = -0.1;
            scene.add(ground);
            
            // Grid and axes
            scene.add(new THREE.GridHelper(150, 30, 0x444444, 0x333333));
            scene.add(new THREE.AxesHelper(10));
            
            this.scenes[type] = scene;
            this.cameras[type] = camera;
            this.renderers[type] = renderer;
            this.controls[type] = controls;
        });
        
        window.addEventListener('resize', () => this.onWindowResize());
    }
    
    setupControls() {
        document.getElementById('frame-slider').addEventListener('input', (e) => {
            this.loadFrame(parseInt(e.target.value));
        });
        
        document.getElementById('play-btn').addEventListener('click', () => this.togglePlay());
        document.getElementById('prev-btn').addEventListener('click', () => this.previousFrame());
        document.getElementById('next-btn').addEventListener('click', () => this.nextFrame());
        document.getElementById('reset-view-btn').addEventListener('click', () => this.resetView());
    }
    
    loadFrame(frameIndex) {
        this.currentFrame = frameIndex;
        
        // Get frame info from detection data
        const detFrame = this.data['det'][frameIndex];
        const actualFrameId = detFrame?.frame_id ?? '-';
        const sequenceName = detFrame?.sequence_name ?? '-';
        
        this.types.forEach(type => {
            this.clearBoxes(this.scenes[type]);
            
            const frame = this.data[type][frameIndex];
            if (frame && frame.boxes) {
                frame.boxes.forEach(box => this.addBox(this.scenes[type], box));
                
                const avgScore = frame.boxes.length > 0 
                    ? (frame.boxes.reduce((s, b) => s + b.score, 0) / frame.boxes.length).toFixed(3)
                    : '0.000';
                
                document.getElementById(`stats-${type}`).textContent = 
                    `${frame.boxes.length} boxes | avg: ${avgScore}`;
            }
        });
        
        // Update UI
        document.getElementById('det-boxes').textContent = this.data['det'][frameIndex]?.boxes?.length || 0;
        document.getElementById('grm-prm-boxes').textContent = this.data['grm-prm'][frameIndex]?.boxes?.length || 0;
        document.getElementById('full-boxes').textContent = this.data['full'][frameIndex]?.boxes?.length || 0;
        
        document.getElementById('frame-slider').value = frameIndex;
        document.getElementById('frame-number').textContent = frameIndex;
        document.getElementById('current-frame').textContent = 
            `${frameIndex} / ${this.data['det'].length}`;
        document.getElementById('actual-frame-id').textContent = actualFrameId;
        document.getElementById('sequence-name').textContent = sequenceName;
    }
    
    clearBoxes(scene) {
        const toRemove = [];
        scene.traverse(obj => {
            if (obj.userData.isBox) toRemove.push(obj);
        });
        toRemove.forEach(obj => scene.remove(obj));
    }
    
    addBox(scene, box) {
        const { center, size, rotation, score } = box;
        
        const geometry = new THREE.BoxGeometry(size[0], size[2], size[1]);
        const color = score > 0.9 ? 0x00ff00 : score > 0.7 ? 0xffff00 : 0xff0000;
        
        const material = new THREE.MeshStandardMaterial({
            color: color,
            transparent: true,
            opacity: 0.3,
            side: THREE.DoubleSide
        });
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(center[0], center[2], center[1]);
        mesh.rotation.y = rotation;
        
        const edges = new THREE.EdgesGeometry(geometry);
        const lineMaterial = new THREE.LineBasicMaterial({ color: color, linewidth: 2 });
        mesh.add(new THREE.LineSegments(edges, lineMaterial));
        
        mesh.userData.isBox = true;
        scene.add(mesh);
    }
    
    togglePlay() {
        this.isPlaying = !this.isPlaying;
        const btn = document.getElementById('play-btn');
        
        if (this.isPlaying) {
            btn.textContent = '⏸️ Pause';
            this.playInterval = setInterval(() => {
                this.nextFrame();
                if (this.currentFrame >= this.data['det'].length - 1) {
                    this.togglePlay();
                }
            }, 200);
        } else {
            btn.textContent = '▶️ Play';
            clearInterval(this.playInterval);
        }
    }
    
    previousFrame() {
        if (this.currentFrame > 0) {
            this.loadFrame(this.currentFrame - 1);
        }
    }
    
    nextFrame() {
        if (this.currentFrame < this.data['det'].length - 1) {
            this.loadFrame(this.currentFrame + 1);
        }
    }
    
    resetView() {
        this.types.forEach(type => {
            this.cameras[type].position.set(50, 50, 50);
            this.cameras[type].lookAt(0, 0, 0);
            this.controls[type].reset();
        });
    }
    
    onWindowResize() {
        this.types.forEach(type => {
            const container = document.getElementById(`canvas-${type}`);
            this.cameras[type].aspect = container.clientWidth / container.clientHeight;
            this.cameras[type].updateProjectionMatrix();
            this.renderers[type].setSize(container.clientWidth, container.clientHeight);
        });
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.types.forEach(type => {
            this.controls[type].update();
            this.renderers[type].render(this.scenes[type], this.cameras[type]);
        });
    }
}

window.addEventListener('DOMContentLoaded', () => {
    new AblationViewer();
});
