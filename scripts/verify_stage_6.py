 # python -m scripts.verify_stage_6


from ai_slop_gate.providers.terraform_static import TerraformStaticProvider
from ai_slop_gate.providers.k8s_static import KubernetesStaticProvider

print("▶️ Terraform provider")
tf = TerraformStaticProvider()
tf_obs = tf.collect()
print(f"Observations: {len(tf_obs)}")

print("▶️ Kubernetes provider")
k8s = KubernetesStaticProvider()
k8s_obs = k8s.collect()
print(f"Observations: {len(k8s_obs)}")

print("✅ Stage 6 OK")
