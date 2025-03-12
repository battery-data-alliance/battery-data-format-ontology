
.. toctree::
   :includehidden:
   :hidden:

   Class Index <battery-data-format>
   Get Started <pages/getstarted>
   Examples <pages/examples>
   About <pages/about>
   FAQ <pages/faq>

Battery Data Format Ontology
================================

Welcome to the **Battery Data Format Ontology**, a semantic resource to improve the machine-readability and interoperability of battery data. **Here's a simple example:**

.. tab-set::

   .. tab-item:: JSON

      .. code-block:: json
         :linenos:

         {
            "@context": "https://w3id.org/emmo/domain/electrochemistry/context",
            "@type": "ElectrochemicalCell",
            "hasNegativeElectrode": {
               "@type": "ZincElectrode"
            },
            "hasPositiveElectrode": {
               "@type": "ManganeseDioxideElectrode"
            },
            "hasElectrolyte": {
               "@type": "AlkalineElectrolyte"
            }
         }

   .. tab-item:: JSON-LD Playground

      .. raw:: html
            
         <div style="position: relative; padding-top: 56.25%;">  <!-- Aspect ratio of 16:9 -->
            <iframe src="https://json-ld.org/playground/#startTab=tab-expanded&json-ld=%7B%22%40context%22%3A%22https%3A%2F%2Fraw.githubusercontent.com%2Femmo-repo%2Fdomain-electrochemistry%2Fmaster%2Fcontext.json%22%2C%22%40type%22%3A%22ElectrochemicalCell%22%2C%22hasNegativeElectrode%22%3A%7B%22%40type%22%3A%22ZincElectrode%22%7D%2C%22hasPositiveElectrode%22%3A%7B%22%40type%22%3A%22ManganeseDioxideElectrode%22%7D%2C%22hasElectrolyte%22%3A%7B%22%40type%22%3A%22AlkalineElectrolyte%22%7D%7D" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" frameborder="0" allowfullscreen></iframe>
         </div>



Check out these resources to get started!
-----------------------------------------
.. grid::

    .. grid-item-card::
        :link: pages/getstarted.html

        :octicon:`rocket;1em;sd-text-info`  Get Started
        ^^^^^^^^^^^
        Let's go! Here is some information to help you get started

    .. grid-item-card::
        :link: pages/electrochemistry.html

        :octicon:`book;1em;sd-text-info`  Class Index
        ^^^^^^^^^^^
        A complete list of terms and some human-readable annotations

.. grid::

    .. grid-item-card::
        :link: pages/examples.html

        :octicon:`pencil;1em;sd-text-info`  Examples
        ^^^^^^^^
        Here are some examples that demonstrate basic usage of the ontology

    .. grid-item-card::
        :link: pages/contribute.html

        :octicon:`thumbsup;1em;sd-text-info`  Contribute
        ^^^^^^^^^^
        Help us develop the ontology by following these guidelines
