using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;

namespace Parabox.OD
{
	public class ODCopyPastePreferences
	{
		private static bool m_Initialized = false;
		private static bool m_ConvertToRightHandedOnCopy;
		private static bool m_ConvertToLeftHandedOnPaste;
		private static bool m_SplitVerticesOnPaste;

		private static void InitializePreferences()
		{
			m_ConvertToRightHandedOnCopy = EditorPrefs.GetBool(ODCopyPaste.ConvertToRightHandedOnCopy, false);
			m_ConvertToLeftHandedOnPaste = EditorPrefs.GetBool(ODCopyPaste.ConvertToLeftHandedOnPaste, false);
			m_SplitVerticesOnPaste = EditorPrefs.GetBool(ODCopyPaste.SplitVerticesOnPaste, true);
			m_Initialized = true;
		}

		[PreferenceItem("OD Copy Paste")]
		private static void OnGUI()
		{
			if(!m_Initialized)
				InitializePreferences();

			EditorGUI.BeginChangeCheck();

			GUILayout.Label("Copy", EditorStyles.boldLabel);
			m_ConvertToRightHandedOnCopy = EditorGUILayout.Toggle("Convert To Right Handed", m_ConvertToRightHandedOnCopy);
			GUILayout.Label("Paste", EditorStyles.boldLabel);
			m_ConvertToLeftHandedOnPaste = EditorGUILayout.Toggle("Convert To Left Handed", m_ConvertToLeftHandedOnPaste);
			m_SplitVerticesOnPaste = EditorGUILayout.Toggle("Recalculate Normals", m_SplitVerticesOnPaste);

			if(EditorGUI.EndChangeCheck())
			{
				EditorPrefs.SetBool(ODCopyPaste.ConvertToRightHandedOnCopy, m_ConvertToRightHandedOnCopy);
				EditorPrefs.SetBool(ODCopyPaste.ConvertToLeftHandedOnPaste, m_ConvertToLeftHandedOnPaste);
				EditorPrefs.SetBool(ODCopyPaste.SplitVerticesOnPaste, m_SplitVerticesOnPaste);
			}
		}
	}
}
