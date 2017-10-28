using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Parabox.OD
{
	public static class MeshUtility
	{
		public static int[] TriangulatePolygon(Polygon poly)
		{
			return TriangulatePolygon(poly.indices);
		}

		public static int[] TriangulatePolygon(int[] indices)
		{
			// for now just do a simple fan triangulate
			// in the future it would be nice to do ear clipping
			int[] triangles = new int[(indices.Length - 2) * 3];

			for (int i = 1; i < indices.Length - 1; i++)
			{
				triangles[(i-1)*3+0] = indices[0  ];
				triangles[(i-1)*3+1] = indices[i  ];
				triangles[(i-1)*3+2] = indices[i+1];
			}

			return triangles;
		}

		public static bool GeneratePerTriangleVertices(List<Vector3> positions,
			List<Vector3> normals,
			List<UVCoord> uvCoords,
			List<Polygon> polygons,
			out List<Vertex> vertices,
			out Dictionary<string, List<int>> indices)
		{
			vertices = new List<Vertex>();
			indices = new Dictionary<string, List<int>>();

			var submeshes = new Dictionary<string, List<int>>();
			bool uvsValid = uvCoords.Count > 0;
			// uvs can be a mix of per-poly and continuous uvs
			bool uvsIndexedByPolygon = uvsValid && uvCoords.Any(x => x.polygonIndex > -1);
			int index = 0;

			if (uvsIndexedByPolygon)
			{
				var polygonUvLookup = new Dictionary<int, Dictionary<int, Vector2>>();

				for (int i = 0, uc = uvCoords.Count; i < uc; i++)
				{
					Dictionary<int, Vector2> tri = null;

					if (polygonUvLookup.TryGetValue(uvCoords[i].polygonIndex, out tri))
						tri.Add(uvCoords[i].vertexIndex, uvCoords[i].position);
					else
						polygonUvLookup.Add(uvCoords[i].polygonIndex,
							new Dictionary<int, Vector2>() {{uvCoords[i].vertexIndex, uvCoords[i].position}});
				}

				Dictionary<int, Vector2> fallback = polygonUvLookup.ContainsKey(-1) ? polygonUvLookup[-1] : null;

				for (int ply = 0, tc = polygons.Count; ply < tc; ply++)
				{
					int[] polyIndices = TriangulatePolygon(polygons[ply]);

					List<int> submeshIndices;

					if(!indices.TryGetValue(polygons[ply].material, out submeshIndices))
						indices.Add(polygons[ply].material, submeshIndices = new List<int>());

					for (int n = 0, ic = polyIndices.Length; n < ic; n++)
					{
						Dictionary<int, Vector2> polyUvs;
						Vector2 v;

						int vi = polyIndices[n];
						submeshIndices.Add(index++);

						if ((polygonUvLookup.TryGetValue(ply, out polyUvs) && polyUvs.TryGetValue(polyIndices[n], out v)) ||
						    (fallback != null && fallback.TryGetValue(polyIndices[n], out v)))
						{
							vertices.Add(new Vertex()
							{
								position = positions[vi],
								normal = vi < normals.Count ? normals[vi] : Vector3.zero,
								uv = v
							});
						}
						else
						{
							vertices.Add(new Vertex()
							{
								position = positions[polyIndices[n]],
								normal = vi < normals.Count ? normals[vi] : Vector3.zero
							});
						}
					}
				}
			}

			return true;
		}

		public static Mesh CompileMesh(List<Vertex> vertices, Dictionary<string, List<int>> indices)
		{
			Debug.Log("vertices: " + vertices.Count);
			List<Vector3> positions = vertices.Select(x => x.position).ToList();
			List<Vector3> normals = vertices.Select(x => x.normal).ToList();
			List<Vector2> uvs = vertices.Select(x => x.uv).ToList();

			Mesh m = new Mesh();
			m.SetVertices(positions);
			m.SetNormals(normals);
			m.SetUVs(0, uvs);
			m.subMeshCount = indices.Count;
			int index = 0;
			foreach(var kvp in indices)
				m.SetIndices(kvp.Value.ToArray(), MeshTopology.Triangles, index++);

			return m;
		}
	}
}
