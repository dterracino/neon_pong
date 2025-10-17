"""
Enhanced particle system for visual effects

Supports multiple emission modes, motion patterns, and behaviors
for creating complex particle effects like menu interactions, fireworks,
and ambient effects.
"""
import random
import math
from typing import List, Tuple, Optional, Callable
from enum import Enum


class EmissionMode(Enum):
    """Particle emission modes"""
    BURST = "burst"           # All at once
    CONTINUOUS = "continuous" # Over time
    ORBITAL = "orbital"       # Around a point
    TRAIL = "trail"           # Between two points


class MotionPattern(Enum):
    """Particle motion patterns"""
    RADIAL = "radial"         # Spread outward
    FLOAT = "float"           # Slow upward drift
    ORBITAL = "orbital"       # Circle around point
    DIRECTIONAL = "directional" # Move in specific direction
    FIREWORK = "firework"     # Burst up then fall


class EnhancedParticle:
    """Enhanced particle with more control"""
    
    def __init__(self, x: float, y: float, color: tuple, lifetime: float,
                 velocity_x: float = 0.0, velocity_y: float = 0.0,
                 size: float = 4.0, motion_pattern: MotionPattern = MotionPattern.RADIAL):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.motion_pattern = motion_pattern
        self.age = 0.0
        
        # For orbital motion
        self.orbit_center_x = x
        self.orbit_center_y = y
        self.orbit_radius = 0.0
        self.orbit_angle = 0.0
        self.orbit_speed = 0.0
    
    def update(self, dt: float) -> bool:
        """Update particle based on motion pattern, return False if dead"""
        self.age += dt
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            return False
        
        # Apply motion pattern
        if self.motion_pattern == MotionPattern.RADIAL:
            # Spread outward and slow down
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            self.velocity_x *= 0.98
            self.velocity_y *= 0.98
            
        elif self.motion_pattern == MotionPattern.FLOAT:
            # Float upward with slight horizontal drift
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            # Add some gentle swaying
            self.x += math.sin(self.age * 2.0) * 10.0 * dt
            
        elif self.motion_pattern == MotionPattern.ORBITAL:
            # Orbit around center point
            self.orbit_angle += self.orbit_speed * dt
            self.x = self.orbit_center_x + math.cos(self.orbit_angle) * self.orbit_radius
            self.y = self.orbit_center_y + math.sin(self.orbit_angle) * self.orbit_radius
            
        elif self.motion_pattern == MotionPattern.DIRECTIONAL:
            # Move in direction with no slowdown
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            
        elif self.motion_pattern == MotionPattern.FIREWORK:
            # Burst upward then fall with gravity
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            self.velocity_y += 200.0 * dt  # Gravity
            self.velocity_x *= 0.99
        
        return True
    
    def get_alpha(self) -> float:
        """Get alpha based on remaining lifetime"""
        return self.lifetime / self.max_lifetime


class ParticleEmitter:
    """Individual particle emitter with specific behavior"""
    
    def __init__(self, x: float, y: float, color: tuple,
                 emission_mode: EmissionMode = EmissionMode.BURST,
                 motion_pattern: MotionPattern = MotionPattern.RADIAL):
        self.x = x
        self.y = y
        self.color = color
        self.emission_mode = emission_mode
        self.motion_pattern = motion_pattern
        self.active = True
        
        # Continuous emission settings
        self.emission_rate = 10.0  # particles per second
        self.emission_timer = 0.0
        
        # Particle settings
        self.particle_lifetime = 1.0
        self.particle_size = 4.0
        self.particle_speed = 100.0
        self.particle_spread = 360.0  # degrees
        
        # Orbital settings
        self.orbit_radius = 100.0
        self.orbit_speed = 2.0  # radians per second
        self.orbit_particle_count = 20
    
    def emit_burst(self, count: int) -> List[EnhancedParticle]:
        """Emit a burst of particles"""
        particles = []
        for i in range(count):
            angle = random.uniform(0, math.radians(self.particle_spread))
            speed = random.uniform(self.particle_speed * 0.5, self.particle_speed * 1.5)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            size = random.uniform(self.particle_size * 0.7, self.particle_size * 1.3)
            lifetime = random.uniform(self.particle_lifetime * 0.8, self.particle_lifetime * 1.2)
            
            particle = EnhancedParticle(
                self.x, self.y, self.color, lifetime,
                vx, vy, size, self.motion_pattern
            )
            particles.append(particle)
        
        return particles
    
    def emit_continuous(self, dt: float) -> List[EnhancedParticle]:
        """Emit particles continuously over time"""
        particles = []
        self.emission_timer += dt
        
        particles_to_spawn = int(self.emission_timer * self.emission_rate)
        self.emission_timer -= particles_to_spawn / self.emission_rate
        
        for _ in range(particles_to_spawn):
            angle = random.uniform(0, math.radians(self.particle_spread))
            speed = random.uniform(self.particle_speed * 0.5, self.particle_speed * 1.5)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            size = random.uniform(self.particle_size * 0.7, self.particle_size * 1.3)
            lifetime = random.uniform(self.particle_lifetime * 0.8, self.particle_lifetime * 1.2)
            
            particle = EnhancedParticle(
                self.x, self.y, self.color, lifetime,
                vx, vy, size, self.motion_pattern
            )
            particles.append(particle)
        
        return particles
    
    def emit_orbital(self) -> List[EnhancedParticle]:
        """Create orbital particles around center point"""
        particles = []
        angle_step = (2 * math.pi) / self.orbit_particle_count
        
        for i in range(self.orbit_particle_count):
            angle = i * angle_step + random.uniform(-0.1, 0.1)
            
            particle = EnhancedParticle(
                self.x, self.y, self.color, float('inf'),
                0, 0, self.particle_size, MotionPattern.ORBITAL
            )
            
            # Set orbital parameters
            particle.orbit_center_x = self.x
            particle.orbit_center_y = self.y
            particle.orbit_radius = self.orbit_radius
            particle.orbit_angle = angle
            particle.orbit_speed = self.orbit_speed
            
            particles.append(particle)
        
        return particles


class EnhancedParticleSystem:
    """Enhanced particle system supporting multiple emitters and patterns"""
    
    def __init__(self):
        self.particles: List[EnhancedParticle] = []
        self.emitters: List[ParticleEmitter] = []
    
    def add_emitter(self, emitter: ParticleEmitter):
        """Add a particle emitter"""
        self.emitters.append(emitter)
    
    def remove_emitter(self, emitter: ParticleEmitter):
        """Remove a particle emitter"""
        if emitter in self.emitters:
            self.emitters.remove(emitter)
    
    def clear_emitters(self):
        """Remove all emitters"""
        self.emitters.clear()
    
    def emit_burst(self, x: float, y: float, color: tuple, count: int,
                   lifetime: float = 1.0, speed: float = 100.0,
                   motion_pattern: MotionPattern = MotionPattern.RADIAL):
        """Emit a burst of particles"""
        emitter = ParticleEmitter(x, y, color, EmissionMode.BURST, motion_pattern)
        emitter.particle_lifetime = lifetime
        emitter.particle_speed = speed
        self.particles.extend(emitter.emit_burst(count))
    
    def emit_trail(self, x1: float, y1: float, x2: float, y2: float,
                   color: tuple, count: int, lifetime: float = 0.5):
        """Emit particles along a trail from point 1 to point 2"""
        for i in range(count):
            t = i / max(1, count - 1)
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            
            particle = EnhancedParticle(
                x, y, color, lifetime,
                random.uniform(-20, 20),
                random.uniform(-20, 20),
                random.uniform(2, 4),
                MotionPattern.RADIAL
            )
            self.particles.append(particle)
    
    def create_orbital_ring(self, x: float, y: float, color: tuple,
                           radius: float = 100.0, count: int = 20,
                           speed: float = 2.0, size: float = 4.0):
        """Create a ring of orbital particles"""
        emitter = ParticleEmitter(x, y, color, EmissionMode.ORBITAL, MotionPattern.ORBITAL)
        emitter.orbit_radius = radius
        emitter.orbit_speed = speed
        emitter.orbit_particle_count = count
        emitter.particle_size = size
        
        self.particles.extend(emitter.emit_orbital())
        self.emitters.append(emitter)
    
    def create_continuous_emitter(self, x: float, y: float, color: tuple,
                                  rate: float = 10.0, lifetime: float = 1.0,
                                  speed: float = 50.0, spread: float = 360.0,
                                  motion_pattern: MotionPattern = MotionPattern.FLOAT):
        """Create a continuous particle emitter"""
        emitter = ParticleEmitter(x, y, color, EmissionMode.CONTINUOUS, motion_pattern)
        emitter.emission_rate = rate
        emitter.particle_lifetime = lifetime
        emitter.particle_speed = speed
        emitter.particle_spread = spread
        
        self.emitters.append(emitter)
        return emitter
    
    def emit_firework(self, x: float, y: float, color: tuple,
                     count: int = 50, speed: float = 200.0):
        """Emit firework-style particles"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            particle_speed = random.uniform(speed * 0.5, speed * 1.5)
            
            vx = math.cos(angle) * particle_speed
            vy = math.sin(angle) * particle_speed - 100.0  # Initial upward bias
            
            particle = EnhancedParticle(
                x, y, color,
                random.uniform(1.0, 2.0),
                vx, vy,
                random.uniform(2, 5),
                MotionPattern.FIREWORK
            )
            self.particles.append(particle)
    
    def update(self, dt: float):
        """Update all particles and emitters"""
        # Update existing particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Update emitters
        for emitter in self.emitters:
            if not emitter.active:
                continue
            
            if emitter.emission_mode == EmissionMode.CONTINUOUS:
                new_particles = emitter.emit_continuous(dt)
                self.particles.extend(new_particles)
    
    def clear(self):
        """Clear all particles"""
        self.particles.clear()
    
    def clear_all(self):
        """Clear all particles and emitters"""
        self.particles.clear()
        self.emitters.clear()
