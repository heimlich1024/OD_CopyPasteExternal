using System;
using NUnit.Framework.Constraints;
using UnityEngine;

namespace Parabox.OD
{
	public struct Vertex : IEquatable<Vertex>
	{
		private const float FLT_COMPARE_RESOLUTION = 1000f;

		public Vector3 position;
		public Vector3 normal;
		public Vector2 uv;

		public override int GetHashCode()
		{
			int hash = 7;

			unchecked
			{
				hash ^= GetHashCode(position);
				hash ^= GetHashCode(normal);
				hash ^= GetHashCode(uv);
			}

			return hash;
		}

		private static int GetHashCode(Vector2 v)
		{
			int x = (int)(v.x * FLT_COMPARE_RESOLUTION);
			int y = (int)(v.y * FLT_COMPARE_RESOLUTION);

			int hash = 7;

			unchecked
			{
				hash = (hash * 7) ^ x;
				hash = (hash * 7) ^ y;
			}
			return hash;
		}

		private static int GetHashCode(Vector3 v)
		{
			int x = (int)(v.x * FLT_COMPARE_RESOLUTION);
			int y = (int)(v.y * FLT_COMPARE_RESOLUTION);
			int z = (int)(v.z * FLT_COMPARE_RESOLUTION);

			int hash = 7;

			unchecked
			{
				hash = (hash * 7) ^ x;
				hash = (hash * 7) ^ y;
				hash = (hash * 7) ^ z;
			}
			return hash;
		}

		public bool Equals(Vertex other)
		{
			return Approx(position, other.position) &&
				Approx(normal, other.normal) &&
				Approx(uv, other.uv);
		}

		private static bool Approx(Vector2 a, Vector2 b)
		{
			return Mathf.Approximately(a.x, b.x) && Mathf.Approximately(a.y, b.y);
		}

		private static bool Approx(Vector3 a, Vector3 b)
		{
			return Mathf.Approximately(a.x, b.x) &&
				Mathf.Approximately(a.y, b.y) &&
				Mathf.Approximately(a.z, b.z);
		}
	}
}