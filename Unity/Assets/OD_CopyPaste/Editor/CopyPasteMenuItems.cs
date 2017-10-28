using UnityEngine;
using UnityEditor;
using System.IO;
using System.Linq;

namespace Parabox.OD
{
	/**
	 * Editor functionality for copy / paste from external.
	 */
	internal static class CopyPasteMenuItems
	{
		private static Material DefaultMaterial()
		{
			GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
			Material mat = go.GetComponent<MeshRenderer>().sharedMaterial;
			Object.DestroyImmediate(go);
			return mat;
		}

		[MenuItem("Edit/Paste Mesh from External %#v")]
		private static void Import()
		{
			Mesh mesh;
			string[] materials;

			if (CopyPaste.Import(CopyPaste.GetTempFile(), out mesh, out materials))
			{
				GameObject go = new GameObject();
				go.AddComponent<MeshFilter>().sharedMesh = mesh;

				if (materials.Length > 0)
				{
					Material[] mats = new Material[materials.Length];
					Material[] all = (Material[]) Resources.FindObjectsOfTypeAll(typeof(Material));
					for (int i = 0, mc = mats.Length; i < mc; i++)
						mats[i] = all.FirstOrDefault(x => x.name.Equals(materials[i])) ?? DefaultMaterial();
					go.AddComponent<MeshRenderer>().sharedMaterials = mats;
				}
				else
				{
					go.AddComponent<MeshRenderer>().sharedMaterial = DefaultMaterial();
				}
			}
			else
			{
				Object.DestroyImmediate(mesh);
			}
		}

		[MenuItem("Edit/Copy Mesh To External %#c")]
		private static void Export()
		{
			GameObject first = Selection.gameObjects.FirstOrDefault(x => x.GetComponent<MeshFilter>() != null);

			if(first != null)
				CopyPaste.Export(
					first.GetComponent<MeshFilter>().sharedMesh,
					first.GetComponent<MeshRenderer>().sharedMaterials);
		}
	}
}
