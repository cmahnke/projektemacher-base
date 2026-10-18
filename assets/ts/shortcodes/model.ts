import * as THREE from 'three/src/Three.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { HalftonePass, type HalftonePassParameters } from 'three/addons/postprocessing/HalftonePass.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';

declare global {
  interface Window {
    initModel: typeof initModel;
  }
  interface HTMLCanvasElement {
    scene?: THREE.Scene;
  }
}

interface ModelSettings {
  halftone: boolean;
  autoRotate: boolean;
  autoRotateSpeed: number;
  minPolarAngle: number;
  maxPolarAngle: number;
  maxDistance: number;
  minDistance: number;
}

let scene: THREE.Scene;
let renderer: THREE.WebGLRenderer;
let camera: THREE.PerspectiveCamera;
let controls: OrbitControls | undefined;
let model: THREE.Object3D | undefined;
let composer: EffectComposer | undefined;

const defaultSettings: ModelSettings = {
  halftone: false,
  autoRotate: true,
  autoRotateSpeed: .01,
  minPolarAngle: deg2rad(15),
  maxPolarAngle:  deg2rad(90),
  maxDistance: 400,
  minDistance: 100,
}

function deg2rad(degrees: number): number {
  return degrees * (Math.PI / 180);
}

/* Control settings */
export function initModel(canvasOrNull: HTMLCanvasElement | null, modelUrl: string, _replacements?: unknown, settings?: Partial<ModelSettings>): void {
  if (canvasOrNull === null) {
    console.log('Model canvas is null!');
    return;
  }
  const canvas = canvasOrNull;
  const modelSettings: ModelSettings = settings !== undefined
    ? {...defaultSettings, ...settings}
    : defaultSettings;

  const loader = new GLTFLoader();
  scene = new THREE.Scene();

  loader.load(modelUrl,
    function (gltf) {
      model = gltf.scene;
      model.position.y = -30.0;
      scene.add(model);

      gltf.cameras.forEach(cam => {
        scene.add(cam);
      });

      const light = new THREE.AmbientLight( 0xffffff, 1.8);
      scene.add( light );
      const directionalLight = new THREE.DirectionalLight( 0xffffff, 0.9 );
      scene.add( directionalLight );

      renderer = new THREE.WebGLRenderer({canvas: canvas, antialias: true});
      const parentWidth = (renderer.domElement.parentNode as HTMLElement).clientWidth;
      const parentHeight = (renderer.domElement.parentNode as HTMLElement).clientHeight;

      const allCameras = scene.getObjectsByProperty('isCamera', true);
      camera = allCameras[Math.floor(Math.random() * allCameras.length)] as THREE.PerspectiveCamera;

      camera.aspect = parentWidth / parentHeight;
      camera.updateProjectionMatrix();

      const ratio = window.devicePixelRatio || 1;
      renderer.setPixelRatio(ratio);

      renderer.setSize(parentWidth, parentHeight);
      renderer.setAnimationLoop(animate);
      renderer.setClearColor(0xffffff, 0);
      controls = new OrbitControls(camera, renderer.domElement);

      controls.autoRotate = modelSettings.autoRotate;
      controls.autoRotateSpeed = modelSettings.autoRotateSpeed;
      controls.minPolarAngle = modelSettings.minPolarAngle;
      controls.maxPolarAngle = modelSettings.maxPolarAngle;
      controls.maxDistance = modelSettings.maxDistance;
      controls.minDistance = modelSettings.minDistance;

      if (modelSettings.halftone) {
        composer = postprocess(renderer, scene, camera, parentWidth, parentHeight)
      }

      window.addEventListener("resize", () => {
        const parent = canvas.parentNode as HTMLElement;
        camera.aspect = parent.clientWidth / parent.clientHeight;
        camera.updateProjectionMatrix();
        if (composer !== undefined) {
          composer.setSize(parent.clientWidth, parent.clientHeight);
        }
        renderer.setSize(parent.clientWidth, parent.clientHeight);
      });

      canvas.scene = scene;

  	},
    undefined,
  	function (error) {
  		console.log('An error happened', error);
  	}
  );

};

function animate(): void {
  setTimeout( function() {
    requestAnimationFrame( animate );
  }, 1000 / 30 );

	// required if controls.enableDamping or controls.autoRotate are set to true
  if (controls !== undefined) {
	  controls.update();
  }
  if (composer === undefined) {
    renderer.render(scene, camera);
  } else {
    composer.render()
  }
}

function postprocess(renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.PerspectiveCamera, width: number, height: number): EffectComposer {
  const composer = new EffectComposer(renderer);
  const renderPass = new RenderPass(scene, camera);
  const params = {
    shape: 1,
    radius: 7,
    rotateR: Math.PI / 12,
    rotateB: Math.PI / 12 * 2,
    rotateG: Math.PI / 12 * 3,
    scatter: 0,
    blending: 1,
    blendingMode: 7,
    greyscale: false,
    disable: false
  };
  const halftoneParams: HalftonePassParameters & { width: number; height: number } = { ...params, width: width, height: height };
  const halftonePass = new HalftonePass(halftoneParams);
  composer.addPass(renderPass);
  composer.addPass(halftonePass);
  return composer;
}

window.initModel = initModel;
