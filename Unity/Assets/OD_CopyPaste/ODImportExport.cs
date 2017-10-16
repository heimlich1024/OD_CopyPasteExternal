using System.Collections;
using System.Collections.Generic;
using System;
using System.IO;
using UnityEngine;
/**
 * todo
 * 	- deleting pasted meshes will leak in editor (but adding a DestroyImmediate will break Undo...)
 *  - easier way to enable/disable handedness swapping
 * 	- handle multiple selected meshes (by merging to a single mesh w/ transforms applied)
 * 	- support importing materials, bone weights, uvs
 * 	- keep submeshes imported as quads in quad topology
 */

namespace Parabox.OD
{
	/**
	 * OD file import & export.
	 */
	public static class ODImportExport
	{
		// Swap handed-ness on import/export?
		private static bool ConvertHandedness
		{
			get
			{
				return false;
			}
		}

		// Split vertices on import?
		private static bool SplitVertices
		{
			get
			{
				return true;
			}
		}

		/**
		 * todo documentation
		 */
		private enum MeshAttribute
		{
			Position,
			Normal,
			Polygon,
			Weight,
			Morph,
			Uv,
			Null
		}

		/**
		 *	Get path to the OD Vertex Data temp file.
		 */
		public static string GetTempFile()
		{
			return string.Format("{0}ODVertexData.txt", Path.GetTempPath());
		}

		/**
		 *	Import from ODVertexData file.
		 */
		public static Mesh Import(string path)
		{
			MeshAttribute attrib = MeshAttribute.Null;
			List<Vector3> positions = new List<Vector3>();
			List<Vector3> normals = new List<Vector3>();
			List<int> polygons = new List<int>();

			using (StreamReader reader = new StreamReader(path))
			{
				for(string line = reader.ReadLine(); line != null; line = reader.ReadLine())
				{
					if(TryParseAttrib(line, ref attrib))
						continue;

					if(attrib == MeshAttribute.Position)
						TryParseVector3(line, positions);
					else if(attrib == MeshAttribute.Normal)
						TryParseVector3(line, normals);
					else if(attrib == MeshAttribute.Polygon)
						TryParsePolygon(line, polygons);
				}
			}

			Mesh m = new Mesh();
			m.name = "ODCopyPaste_Mesh";

			// If normals aren't present then this mesh is probably sharing vertex positions, so split them up and
			// recalculate hard edges.
			if (SplitVertices || normals.Count != positions.Count)
			{
				Vector3[] splitVertices = new Vector3[polygons.Count];
				int[] splitTriangles = new int[polygons.Count];

				for (int i = 0; i < polygons.Count; i++)
				{
					splitVertices[i] = positions[polygons[i]];
					splitTriangles[i] = i;
				}

				m.vertices = splitVertices;
				m.triangles = splitTriangles;
				m.RecalculateNormals();
			}
			else
			{
				m.vertices = positions.ToArray();
				m.triangles = polygons.ToArray();
				m.normals = normals.ToArray();
			}

			m.RecalculateTangents();
			m.RecalculateBounds();

			return m;
		}

		public static void Export(Mesh m, Material[] sharedMaterials)
		{
			if(m == null)
				return;

			int polyCount = 0;

			for (int i = 0; i < m.subMeshCount; i++)
			{
				MeshTopology topo = m.GetTopology(i);
				if (topo == MeshTopology.Triangles)
					polyCount += (int) m.GetIndexCount(i) / 3;
				else if(topo == MeshTopology.Quads)
					polyCount += (int) m.GetIndexCount(i) / 4;
				else
					return;
			}

			using (StreamWriter sw = new StreamWriter(GetTempFile(), false))
			{
				Vector3[] positions = m.vertices;
				Vector3[] normals = m.normals;

				sw.WriteLine(string.Format("VERTICES:{0}", m.vertexCount));

				foreach(Vector3 p in positions)
					sw.WriteLine(string.Format("{0} {1} {2}", ConvertHandedness ? -p.x : p.x, p.y, p.z));

				if (normals != null)
				{
					sw.WriteLine(string.Format("VERTEXNORMALS:{0}", m.vertexCount));

					foreach(Vector3 n in normals)
						sw.WriteLine(string.Format("{0} {1} {2}", ConvertHandedness ? -n.x : n.x, n.y, n.z));
				}

				for (int i = 0; i < m.subMeshCount; i++)
				{
					sw.WriteLine(string.Format("POLYGONS:{0}", polyCount));

					Material material = sharedMaterials != null && sharedMaterials.Length > 0
						? sharedMaterials[i % sharedMaterials.Length]
						: null;

					switch (m.GetTopology(i))
					{
						case MeshTopology.Triangles:
							int[] tris = m.GetIndices(i);
							for (int t = 0; t < tris.Length; t += 3)
								sw.WriteLine(string.Format(
									ConvertHandedness
									? "{2},{1},{0};;{3};;FACE"
									: "{0},{1},{2};;{3};;FACE",
									tris[t],
									tris[t + 1],
									tris[t + 2],
									material == null ? "Default" : material.name));
							break;

						case MeshTopology.Quads:
							int[] quads = m.GetIndices(i);
							for (int t = 0; t < quads.Length; t += 4)
								sw.WriteLine(string.Format(
									ConvertHandedness
									? "{3},{2},{1},{0};;{4};;FACE"
									: "{0},{1},{2},{3};;{4};;FACE",
									quads[t],
									quads[t + 1],
									quads[t + 2],
									quads[t + 3],
									material == null ? "Default" : material.name));
							break;

						default:
							// how'd you get here?
							break;
					}
				}
			}
		}

		private static bool TryParseAttrib(string line, ref MeshAttribute attrib)
		{
			if(line.StartsWith("VERTICES"))
				attrib = MeshAttribute.Position;
			else if(line.StartsWith("VERTEXNORMALS"))
				attrib = MeshAttribute.Normal;
			else if(line.StartsWith("POLYGONS"))
				attrib = MeshAttribute.Polygon;
			else if(line.StartsWith("WEIGHT"))
				attrib = MeshAttribute.Weight;
			else if(line.StartsWith("MORPH"))
				attrib = MeshAttribute.Morph;
			else if(line.StartsWith("UV"))
				attrib = MeshAttribute.Uv;
			else
				return false;

			return true;
		}

		private static bool TryParseVector3(string line, List<Vector3> positions)
		{
			try
			{
				string[] split = line.Trim().Split(' ');
				Vector3 v;
				float.TryParse(split[0], out v.x);
				float.TryParse(split[1], out v.y);
				float.TryParse(split[2], out v.z);
				positions.Add(v);
			}
			catch
			{
				return false;
			}

			return true;
		}

		private static bool TryParsePolygon(string line, List<int> polygons)
		{
			string[] POLYGON_SEPARATOR = new string[] { ";;" };

			try
			{
				// Comma separated list of each vertid in the polygon;;materialname;;polytype.
				// (which can be FACE, SubD, or CCSS)
				// 0,1,2,3;;Default;;FACE
				//
				// For now Unity paste only supports PolyType Face
				string[] split = line.Split(POLYGON_SEPARATOR, StringSplitOptions.RemoveEmptyEntries);

				if(split[2].Equals("FACE"))
				{
					string[] face = split[0].Split(',');
					int[] indices = new int[face.Length];

					for(int i = 0; i < face.Length; i++)
						int.TryParse(face[i], out indices[i]);

					polygons.AddRange( MeshUtility.TriangulatePolygon(indices) );
				}
			}
			catch(Exception e)
			{
				Debug.LogError(e.ToString());
				return false;
			}

			return true;
		}
	}
}
